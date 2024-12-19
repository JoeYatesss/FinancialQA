from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
import numpy as np
from datetime import datetime
import re
from collections import defaultdict

class EnhancedRetriever:
    def __init__(self, vector_store: FAISS):
        self.vector_store = vector_store
        self.conversation_cache = {}
        
    def hybrid_search(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword-based approaches
        """
        print(f"\n=== Performing Hybrid Search for: {query} ===")
        
        # Enhance query with chat history context
        enhanced_query = self._enhance_query(query, chat_history)
        print(f"Enhanced query: {enhanced_query}")
        
        # Perform semantic search
        semantic_results = self.vector_store.similarity_search_with_score(
            enhanced_query,
            k=k*2  # Get more results for reranking
        )
        
        # Extract financial entities for keyword matching
        query_entities = self._extract_financial_entities(query)
        if chat_history:
            for msg in chat_history[-2:]:  # Look at last 2 messages
                hist_entities = self._extract_financial_entities(msg.get('content', ''))
                for key in query_entities:
                    query_entities[key].extend(hist_entities[key])
        
        # Rerank results using hybrid scoring
        ranked_results = self._hybrid_rank(
            semantic_results,
            query_entities
        )
        
        # Group by conversation and maintain context
        final_results = self._group_and_contextualize(ranked_results[:k])
        
        print(f"\nReturning {len(final_results)} contextualized results")
        return final_results
    
    def _enhance_query(self, query: str, chat_history: Optional[List[Dict[str, str]]]) -> str:
        """Enhance the query with relevant context from chat history"""
        if not chat_history:
            return query
            
        # Extract key terms from recent history
        key_terms = set()
        for msg in chat_history[-2:]:  # Look at last 2 messages
            content = msg.get('content', '').lower()
            # Extract numbers and financial terms
            numbers = re.findall(r'\d+(?:\.\d+)?%?', content)
            key_terms.update(numbers)
            
            # Add financial terms
            terms = re.findall(r'\b(increase|decrease|growth|profit|revenue|cost|margin|ratio)\b', content)
            key_terms.update(terms)
        
        # Add relevant terms to query
        if key_terms:
            enhanced_query = f"{query} {' '.join(key_terms)}"
            return enhanced_query
        return query
    
    def _extract_financial_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities for matching"""
        entities = {
            "numbers": [],
            "currency": [],
            "percentages": [],
            "financial_terms": [],
            "years": []
        }
        
        # Extract currency values (handling $ format)
        currency = re.findall(r'\$\s*\d+(?:,\d{3})*(?:\.\d+)?', text)
        entities["currency"] = [c.replace('$', '').replace(',', '').strip() for c in currency]
        
        # Extract percentages (including negative values)
        percentages = re.findall(r'-?\d+(?:\.\d+)?%', text)
        entities["percentages"] = [p.replace('%', '') for p in percentages]
        
        # Extract years
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        entities["years"] = years
        
        # Extract plain numbers (including negative values and commas)
        numbers = re.findall(r'-?\d+(?:,\d{3})*(?:\.\d+)?', text)
        # Filter out numbers that are already captured as currency or years
        clean_numbers = []
        for n in numbers:
            n_clean = n.replace(',', '')
            if (n_clean not in entities["currency"] and 
                n not in entities["years"] and 
                n_clean not in entities["percentages"]):
                clean_numbers.append(n_clean)
        entities["numbers"] = clean_numbers
        
        # Extract financial terms with expanded vocabulary
        financial_terms = re.findall(
            r'\b(increase|decrease|change|growth|decline|net sales|revenue|sales|'
            r'margin|profit|loss|total|cost|expense|income|earnings)\b',
            text.lower()
        )
        entities["financial_terms"] = list(set(financial_terms))  # Remove duplicates
        
        return entities
    
    def _hybrid_rank(
        self,
        semantic_results: List[tuple],
        query_entities: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Rerank results using both semantic and keyword matching scores"""
        ranked_results = []
        
        for doc, semantic_score in semantic_results:
            # Calculate keyword matching score
            doc_entities = doc.metadata.get('financial_entities', {})
            keyword_score = self._calculate_keyword_score(doc_entities, query_entities)
            
            # Combine scores (semantic_score is distance, so lower is better)
            combined_score = (1 / (1 + semantic_score)) * (1 + keyword_score)
            
            ranked_results.append({
                'document': doc,
                'score': combined_score,
                'semantic_score': semantic_score,
                'keyword_score': keyword_score
            })
        
        # Sort by combined score
        ranked_results.sort(key=lambda x: x['score'], reverse=True)
        return ranked_results
    
    def _calculate_keyword_score(
        self,
        doc_entities: Dict[str, List[str]],
        query_entities: Dict[str, List[str]]
    ) -> float:
        """Calculate keyword matching score between document and query entities"""
        score = 0.0
        
        # Score exact matches of numbers and percentages
        for entity_type in ['numbers', 'percentages']:
            matches = set(doc_entities.get(entity_type, [])) & set(query_entities.get(entity_type, []))
            score += len(matches) * 0.5  # Higher weight for exact number matches
        
        # Score financial term matches
        term_matches = set(doc_entities.get('financial_terms', [])) & set(query_entities.get('financial_terms', []))
        score += len(term_matches) * 0.3
        
        return score
    
    def _group_and_contextualize(self, ranked_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group results by conversation and maintain context"""
        conversation_groups = defaultdict(list)
        
        # Group by conversation
        for result in ranked_results:
            doc = result['document']
            doc_id = doc.metadata.get('doc_id')
            conversation_groups[doc_id].append(result)
        
        # Contextualize and select best chunks
        final_results = []
        for doc_id, group in conversation_groups.items():
            # Sort chunks by score and position
            group.sort(key=lambda x: (
                x['score'],
                x['document'].metadata.get('is_first_chunk', False)
            ), reverse=True)
            
            # Take best chunk and its context
            best_chunk = group[0]
            chunk_id = best_chunk['document'].metadata.get('chunk_id')
            
            # Cache conversation context
            if chunk_id not in self.conversation_cache:
                self.conversation_cache[chunk_id] = {
                    'timestamp': datetime.now(),
                    'context': best_chunk['document'].page_content,
                    'metadata': best_chunk['document'].metadata
                }
            
            final_results.append(best_chunk)
        
        return final_results 