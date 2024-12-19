from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import json
import os
from datetime import datetime
from langchain.vectorstores import FAISS

from .embeddings import EnhancedEmbeddingEngine
from .retrieval import EnhancedRetriever
from ..utils.metrics import MetricsTracker
from ..utils.metrics_storage import MetricsStorage

class RAGEngine:
    def __init__(self):
        """Initialize the enhanced RAG engine"""
        try:
            print("\n[RAG Engine] Initializing with fresh metrics...")

            self.embedding_engine = EnhancedEmbeddingEngine()
            self.retriever = None
            self.conversation_memories = {}
            self.metrics_tracker = MetricsTracker()
            self.metrics_storage = MetricsStorage()
            
            self.metrics_tracker.reset()
            print("[RAG Engine] Metrics tracker reset")
            
            self.llm = ChatOpenAI(
                model_name="gpt-4-turbo-preview",
                temperature=0.1,
                max_tokens=2000,
                request_timeout=60
            )
            
            self._initialize_prompts()
            
            self._initialize_vector_store()
            
            print("[RAG Engine] Initialization complete\n")
            
        except Exception as e:
            print(f"Error initializing RAG Engine: {str(e)}")
            raise
    
    def _initialize_prompts(self):
        """Initialize enhanced prompt templates"""
        self.qa_template = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template="""You are a precise financial analyst. Your goal is to provide accurate numerical calculations based on the data provided.

Context Information:
{context}

Chat History:
{chat_history}

Current Question: {question}

Instructions:
1. For financial calculations, always:
   - Use exact numbers from the data
   - Show the final percentage with 2 decimal places
   - For percentage changes: ((New Value - Old Value) / Old Value) * 100
2. When calculating year-over-year changes:
   - Clearly identify the base year and comparison year
   - Use the earlier year as the base for percentage calculations
3. For currency values:
   - Use the exact numbers, ignoring currency symbols
   - Maintain precision in calculations
4. When analyzing trends:
   - Consider the full context provided
   - Note any significant changes or patterns
   - Explain any unusual variations

Your response should be:
- Precise and data-driven
- Include the exact calculation used
- Show the final percentage with 2 decimal places
- Explain any significant context from the data

Please provide your response:"""
        )
    
    def _initialize_vector_store(self):
        """Initialize or load the vector store"""
        vector_store_path = "data/vector_store"
        
        if os.path.exists(f"{vector_store_path}/index.faiss"):
            print("\n=== Loading Existing Vector Store ===")
            try:
                self.embedding_engine.vector_store = FAISS.load_local(
                    folder_path=vector_store_path,
                    embeddings=self.embedding_engine.embeddings
                )
                print("Vector store loaded successfully!")
            except Exception as e:
                print(f"Error loading vector store: {str(e)}")
                print("Will create new vector store...")
                self._create_new_vector_store()
        else:
            print("\n=== Creating New Vector Store ===")
            self._create_new_vector_store()
        
        self.retriever = EnhancedRetriever(self.embedding_engine.vector_store)
    
    def _create_new_vector_store(self):
        """Create a new vector store from training data"""
        if os.path.exists("train.json"):
            with open("train.json", "r") as f:
                data = json.load(f)
            self.embedding_engine.process_documents(data)
        else:
            raise FileNotFoundError("No training data found at train.json")
    
    async def process_question(
        self,
        question: str,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a question using the enhanced RAG pipeline"""
        try:
            print("\n[RAG Engine] Processing question, tracking metrics...")
            start_time = datetime.now()
            
            question_tokens = self.metrics_tracker.track_tokens(question)
            print(f"[RAG Engine] Question tokens: {question_tokens}")
            
            if conversation_id not in self.conversation_memories:
                print("[RAG Engine] New conversation started")
                self.conversation_memories[conversation_id] = {
                    'memory': ConversationBufferMemory(
                        memory_key="chat_history",
                        input_key="question",
                        output_key="answer",
                        return_messages=True
                    ),
                    'context': {},
                    'metrics': {
                        'questions_asked': 0,
                        'total_tokens': 0,
                        'average_response_time': 0
                    }
                }
                self.metrics_tracker.metrics["total_conversations"] += 1
            
            conversation_data = self.conversation_memories[conversation_id]
            
            chat_history = []
            if context and 'history' in context:
                chat_history = context['history']
            
            search_results = self.retriever.hybrid_search(
                query=question,
                chat_history=chat_history
            )
            
            if search_results:
                print("[RAG Engine] Successful retrieval, updating metrics...")
                self.metrics_tracker.metrics["successful_retrievals"] += 1
            
            if not (context and 'relevant_docs' in context):
                context = context or {}
                context['relevant_docs'] = [
                    doc['document'].metadata.get('doc_id', '')
                    for doc in search_results[:3] if doc['score'] > 0.7
                ]
            
            print("[RAG Engine] Calculating retrieval metrics...")
            retrieval_metrics = self.metrics_tracker.calculate_retrieval_metrics(
                retrieved_docs=search_results,
                relevant_docs=context['relevant_docs']
            )
            
            retrieved_context = self._prepare_context(search_results)
            
            prompt = self.qa_template.format(
                context=retrieved_context,
                chat_history=self._format_chat_history(chat_history),
                question=question
            )
            
            prompt_tokens = self.metrics_tracker.track_tokens(prompt)
            print(f"[RAG Engine] Prompt tokens: {prompt_tokens}")
            
            response = await self.llm.ainvoke(prompt)
            answer = response.content
            
            response_tokens = self.metrics_tracker.track_tokens(answer)
            print(f"[RAG Engine] Response tokens: {response_tokens}")
            
            print("[RAG Engine] Calculating ROUGE scores with retrieved context...")
            rouge_scores = self.metrics_tracker.calculate_rouge_with_context(
                answer=answer,
                context=retrieved_context
            )
            print(f"[RAG Engine] Context ROUGE scores: R1={rouge_scores['rouge1']:.2%}, R2={rouge_scores['rouge2']:.2%}, RL={rouge_scores['rougeL']:.2%}")
            
            if not (context and 'ground_truth' in context) and chat_history:
                last_answer = next((msg['content'] for msg in reversed(chat_history) 
                                 if msg.get('role') == 'assistant'), None)
                if last_answer:
                    print("[RAG Engine] Using previous answer as ground truth")
                    context = context or {}
                    context['ground_truth'] = last_answer
            
            if not (context and 'ground_truth' in context):
                print("[RAG Engine] Using retrieved context as ground truth")
                context = context or {}
                context['ground_truth'] = retrieved_context
            
            print("[RAG Engine] Calculating answer metrics...")
            answer_metrics = self.metrics_tracker.calculate_answer_metrics(
                predicted_answer=answer,
                ground_truth=context['ground_truth'],
                embeddings=self.embedding_engine.embeddings
            )
            print(f"[RAG Engine] Answer metrics: {answer_metrics}")
            
            context_retention = 1.0
            if chat_history:
                print("[RAG Engine] Calculating context retention...")
                context_retention = self.metrics_tracker.calculate_context_retention(
                    current_answer=answer,
                    conversation_history=[msg['content'] for msg in chat_history],
                    embeddings=self.embedding_engine.embeddings
                )
                print(f"[RAG Engine] Context retention: {context_retention:.2%}")

            conversation_data['memory'].save_context(
                {"question": question},
                {"answer": answer}
            )
            
            end_time = datetime.now()
            print("[RAG Engine] Calculating response time...")
            response_time = self.metrics_tracker.track_response_time(start_time)
            
            print("[RAG Engine] Updating aggregate metrics...")
            self.metrics_tracker.metrics["total_questions"] += 1
            
            self._update_metrics(conversation_data['metrics'], response_time)
            
            print("[RAG Engine] Getting aggregate metrics...")
            all_metrics = self.metrics_tracker.get_aggregate_metrics()
            conversation_data['metrics'].update(all_metrics)
            
            print(f"[RAG Engine] Storing updated metrics with {all_metrics['total_tokens']} total tokens")
            self.metrics_storage.update_metrics(all_metrics)
            
            return {
                'answer': answer,
                'context': retrieved_context,
                'metrics': all_metrics,
                'search_results': [
                    {
                        'content': r['document'].page_content[:200] + "...",
                        'score': r['score'],
                        'metadata': r['document'].metadata
                    }
                    for r in search_results[:3]
                ]
            }
            
        except Exception as e:
            print(f"Error processing question: {str(e)}")
            raise
    
    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Prepare context from search results with enhanced formatting"""
        context_parts = []
        
        for result in search_results:
            doc = result['document']
            score = result['score']
            
            if score > 0.5:
                context_parts.append(
                    f"[Relevance: {score:.2f}]\n{doc.page_content}\n"
                )
        
        return "\n---\n".join(context_parts)
    
    def _format_chat_history(self, chat_history: List[Dict[str, str]]) -> str:
        """Format chat history for context window"""
        if not chat_history:
            return "No previous conversation."
        
        formatted_history = []
        for msg in chat_history[-3:]:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            formatted_history.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(formatted_history)
    
    def _update_metrics(self, metrics: Dict[str, Any], response_time: float):
        """Update conversation metrics"""
        metrics['questions_asked'] += 1
        
        current_avg = metrics['average_response_time']
        metrics['average_response_time'] = (
            (current_avg * (metrics['questions_asked'] - 1) + response_time)
            / metrics['questions_asked']
        )
    
    def get_metrics(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for a conversation or all conversations"""
        if conversation_id and conversation_id in self.conversation_memories:
            return self.conversation_memories[conversation_id]['metrics']
        
        aggregate_metrics = self.metrics_tracker.get_aggregate_metrics()
        
        aggregate_metrics.update({
            'total_conversations': len(self.conversation_memories),
            'total_questions': sum(
                conv['metrics']['questions_asked'] 
                for conv in self.conversation_memories.values()
            ),
            'total_tokens': sum(
                conv['metrics']['total_tokens'] 
                for conv in self.conversation_memories.values()
            )
        })
        
        self.metrics_storage.update_metrics(aggregate_metrics)
        
        return self.metrics_storage.get_metrics()