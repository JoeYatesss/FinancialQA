import pandas as pd
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from tqdm import tqdm
import time
from functools import partial

class DocumentProcessor:
    def __init__(self):
        self.processed_docs = []
        
    def process_table(self, table_data: Dict[str, Any]) -> str:
        """Convert table data to a structured string format"""
        if not table_data:
            return ""
            
        try:
            # Convert to pandas DataFrame for better handling
            df = pd.DataFrame(table_data)
            
            # Format as markdown table
            table_str = df.to_markdown(index=False)
            return f"\nTable:\n{table_str}\n"
        except Exception as e:
            print(f"Error processing table: {e}")
            return str(table_data)
            
    def process_annotations(self, annotations: Dict[str, Any]) -> Dict[str, Any]:
        """Process and structure annotations"""
        processed = {
            "original_question": annotations.get("original_program", ""),
            "dialogue_turns": [],
            "execution_results": []
        }
        
        # Process dialogue turns
        dialogue_breaks = annotations.get("dialogue_break", [])
        turn_programs = annotations.get("turn_program", [])
        qa_splits = annotations.get("qa_split", [])
        exe_results = annotations.get("exe_ans_list", [])
        
        for i, (turn, program, split, result) in enumerate(zip(
            dialogue_breaks, turn_programs, qa_splits, exe_results
        )):
            processed["dialogue_turns"].append({
                "question": turn,
                "program": program,
                "qa_split": split,
                "result": result
            })
            
        return processed
        
    def process_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single document with all its components"""
        processed = {
            "id": doc.get("id", ""),
            "content": "",
            "metadata": {}
        }
        
        # Process pre-text
        if pre_text := doc.get("pre_text"):
            processed["content"] += f"Context:\n{pre_text}\n\n"
            
        # Process table
        if table := doc.get("table"):
            processed["content"] += self.process_table(table)
            
        # Process post-text
        if post_text := doc.get("post_text"):
            processed["content"] += f"\nAdditional Information:\n{post_text}"
            
        # Process annotations
        if annotations := doc.get("annotation"):
            processed["metadata"]["annotations"] = self.process_annotations(annotations)
            
        # Add original QA pairs
        if qa := doc.get("qa"):
            processed["metadata"]["qa"] = qa
        if qa_0 := doc.get("qa_0"):
            processed["metadata"]["qa_0"] = qa_0
        if qa_1 := doc.get("qa_1"):
            processed["metadata"]["qa_1"] = qa_1
            
        return processed
        
    def _process_document_with_retry(self, doc: Dict[str, Any], max_retries: int = 3) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Process a single document with retry mechanism"""
        doc_id = doc.get("id", "unknown")
        for attempt in range(max_retries):
            try:
                processed = self.process_document(doc)
                return doc_id, processed
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Failed to process document {doc_id} after {max_retries} attempts: {str(e)}")
                    return doc_id, None
                time.sleep(1 * (attempt + 1))  # Exponential backoff
        return doc_id, None

    def batch_process(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 100,
        max_workers: Optional[int] = None,
        show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """Process a batch of documents in parallel with improved error handling and progress tracking
        
        Args:
            documents: List of documents to process
            batch_size: Number of documents to process in each batch
            max_workers: Maximum number of worker processes (defaults to CPU count)
            show_progress: Whether to show progress bar
            
        Returns:
            List of processed documents
        """
        if not documents:
            return []

        # Initialize parameters
        max_workers = max_workers or mp.cpu_count()
        total_docs = len(documents)
        self.processed_docs = []
        failed_docs = []
        
        # Process documents in batches
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create progress bar if requested
            pbar = tqdm(total=total_docs, disable=not show_progress)
            
            # Process documents in batches to manage memory
            for i in range(0, total_docs, batch_size):
                batch = documents[i:min(i + batch_size, total_docs)]
                
                # Submit batch for processing
                future_to_doc = {
                    executor.submit(self._process_document_with_retry, doc): doc
                    for doc in batch
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_doc):
                    doc_id, result = future.result()
                    if result is not None:
                        self.processed_docs.append(result)
                    else:
                        failed_docs.append(doc_id)
                    pbar.update(1)
            
            pbar.close()
        
        # Log processing summary
        success_count = len(self.processed_docs)
        fail_count = len(failed_docs)
        logging.info(f"Batch processing completed: {success_count} succeeded, {fail_count} failed")
        if failed_docs:
            logging.warning(f"Failed document IDs: {failed_docs}")
        
        return self.processed_docs
        
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a processed document by its ID"""
        for doc in self.processed_docs:
            if doc["id"] == doc_id:
                return doc
        return None 