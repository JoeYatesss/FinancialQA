from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import numpy as np
import json
import os
from datetime import datetime
import time
from tqdm import tqdm

class EnhancedEmbeddingEngine:
    def __init__(self, model="text-embedding-3-small"):
        self.embeddings = OpenAIEmbeddings(
            model=model,
            chunk_size=100,  # Smaller chunk size
            max_retries=5,
            request_timeout=60,
            show_progress_bar=True
        )
        
        # Optimized text splitter for financial conversations
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Smaller chunks
            chunk_overlap=100,  # Smaller overlap
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.vector_store = None
        self.batch_size = 5  # Smaller batch size
        
    def process_documents(self, data: List[Dict[str, Any]], save_path: str = "data/vector_store"):
        """Process documents with optimized chunking and embedding strategy"""
        print("\n=== Processing Documents for Embedding ===")
        
        # Create save directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # Load existing vector store if it exists
        if os.path.exists(f"{save_path}/index.faiss"):
            print("Loading existing vector store...")
            try:
                self.vector_store = FAISS.load_local(
                    folder_path=save_path,
                    embeddings=self.embeddings
                )
                print("Existing vector store loaded successfully")
            except Exception as e:
                print(f"Error loading existing vector store: {str(e)}")
                print("Creating new vector store...")
        
        # Process documents in smaller batches with progress bar
        with tqdm(total=len(data), desc="Processing documents") as pbar:
            for batch_start in range(0, len(data), self.batch_size):
                batch_end = min(batch_start + self.batch_size, len(data))
                batch = data[batch_start:batch_end]
                
                batch_texts = []
                batch_metadatas = []
                
                # Process each document in the batch
                for idx, item in enumerate(batch):
                    try:
                        conversation = self._format_conversation(item)
                        chunks = self.text_splitter.split_text(conversation)
                        
                        for chunk_idx, chunk in enumerate(chunks):
                            metadata = {
                                "source": "train.json",
                                "doc_id": str(batch_start + idx),
                                "chunk_id": f"{batch_start + idx}-{chunk_idx}",
                                "timestamp": datetime.now().isoformat(),
                                "original_id": item.get('id'),
                                "chunk_type": "conversation",
                                "total_chunks": len(chunks),
                                "is_first_chunk": chunk_idx == 0,
                                "is_last_chunk": chunk_idx == len(chunks) - 1,
                                "financial_entities": self._extract_financial_entities(chunk)
                            }
                            
                            batch_texts.append(chunk)
                            batch_metadatas.append(metadata)
                    
                    except Exception as e:
                        print(f"\nError processing document {batch_start + idx}: {str(e)}")
                        continue
                
                # Create or update vector store with retry logic
                if batch_texts:
                    success = False
                    max_retries = 5
                    
                    for retry in range(max_retries):
                        try:
                            if self.vector_store is None:
                                self.vector_store = FAISS.from_texts(
                                    texts=batch_texts,
                                    embedding=self.embeddings,
                                    metadatas=batch_metadatas
                                )
                            else:
                                self.vector_store.add_texts(
                                    texts=batch_texts,
                                    metadatas=batch_metadatas
                                )
                            
                            # Save after each successful batch
                            self.vector_store.save_local(save_path)
                            success = True
                            break
                            
                        except Exception as e:
                            print(f"\nRetry {retry + 1}/{max_retries} after error: {str(e)}")
                            if retry < max_retries - 1:
                                wait_time = (retry + 1) * 5  # Exponential backoff
                                print(f"Waiting {wait_time} seconds before retry...")
                                time.sleep(wait_time)
                            else:
                                print("Max retries reached, skipping batch")
                
                if success:
                    pbar.update(len(batch))
                
                # Small delay between batches
                time.sleep(1)
        
        if self.vector_store is None:
            raise Exception("Failed to create vector store")
        
        print("\nProcessing complete!")
        return self.vector_store
    
    def _format_conversation(self, item: Dict[str, Any]) -> str:
        """Format conversation with rich context and clear table structure"""
        try:
            # Extract components with default values
            pre_text = item.get('pre_text', '')
            post_text = item.get('post_text', '')
            table = item.get('table', [])
            annotation = item.get('annotation', {})
            
            # Format text components
            pre_text = '\n'.join(str(x) for x in pre_text) if isinstance(pre_text, list) else str(pre_text)
            post_text = '\n'.join(str(x) for x in post_text) if isinstance(post_text, list) else str(post_text)
            
            # Format table with clear structure
            table_str = "Financial Data Table:\n"
            if table:
                # Add headers with clear separation
                table_str += " | ".join(str(cell) for cell in table[0]) + "\n"
                table_str += "-" * 50 + "\n"
                # Add data rows with proper formatting
                for row in table[1:]:
                    formatted_row = []
                    for cell in row:
                        # Handle currency and percentage formatting
                        if isinstance(cell, str):
                            if '$' in cell:
                                cell = cell.replace(' ', '')  # Remove spaces in currency
                            elif '%' in cell:
                                cell = cell.split('(')[0].strip()  # Take first percentage
                        formatted_row.append(str(cell))
                    table_str += " | ".join(formatted_row) + "\n"
            
            # Build conversation with clear structure and metadata
            conversation_parts = [
                "=== Context ===",
                pre_text.strip(),
                "\n=== Financial Data ===",
                table_str.strip(),
                "\n=== Additional Context ===",
                post_text.strip()
            ]
            
            # Add conversation turns if present
            if 'dialogue_break' in annotation and 'exe_ans_list' in annotation:
                conversation_parts.extend([
                    "\n=== Previous Conversation ===",
                    *[f"Q: {q}\nA: {a}" for q, a in zip(
                        annotation['dialogue_break'],
                        annotation['exe_ans_list']
                    )]
                ])
            
            return "\n".join(filter(None, conversation_parts))
            
        except Exception as e:
            print(f"Error formatting conversation: {str(e)}")
            return str(item)
    
    def _extract_financial_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities for enhanced retrieval"""
        entities = {
            "numbers": [],
            "percentages": [],
            "financial_terms": []
        }
        
        try:
            # Extract numbers and percentages
            words = text.split()
            for word in words:
                if any(c.isdigit() for c in word):
                    if '%' in word:
                        entities["percentages"].append(word)
                    else:
                        entities["numbers"].append(word)
                
                # Basic financial term detection
                if word.lower() in {
                    "increase", "decrease", "growth", "decline", "profit",
                    "revenue", "cost", "margin", "ratio", "total"
                }:
                    entities["financial_terms"].append(word.lower())
            
            # Remove duplicates while preserving order
            for key in entities:
                entities[key] = list(dict.fromkeys(entities[key]))
                
        except Exception as e:
            print(f"Error extracting financial entities: {str(e)}")
        
        return entities