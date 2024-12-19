from typing import Dict, List, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from rouge_score import rouge_scorer
import nltk
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize
from collections import Counter
import tiktoken
import warnings
import re

# Suppress NLTK download messages and warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='Resource punkt_tab not found')

# Download required NLTK data
print("\n[Metrics] Downloading required NLTK data...")
try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    print("[Metrics] NLTK data downloaded successfully")
except Exception as e:
    print(f"[Metrics] Warning: Failed to download NLTK data: {str(e)}")
    print("[Metrics] Will attempt to use existing data")

class MetricsTracker:
    def __init__(self):
        """Initialize metrics tracker with required resources"""
        print("[Metrics Tracker] Initializing...")
        self.reset()
        
        try:
            self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            print("[Metrics Tracker] Initialized successfully")
        except Exception as e:
            print(f"[Metrics Tracker] Warning: Error initializing components: {str(e)}")
            raise
        
    def reset(self):
        """Reset all metrics"""
        self.metrics = {
            # Accuracy metrics
            "answer_accuracy": [],
            "exact_match": [],
            "cosine_similarity": [],
            "rouge_scores": {
                "rouge1": [],
                "rouge2": [],
                "rougeL": []
            },
            
            # Retrieval metrics
            "retrieval_precision": [],
            "retrieval_recall": [],
            "f1_score": [],
            "ndcg": [],
            "mrr": [],
            
            # System metrics
            "response_latency": [],
            "context_retention": [],
            "total_questions": 0,
            "successful_retrievals": 0,
            "total_tokens": 0,
            "total_conversations": 0
        }
        
    def calculate_retrieval_metrics(
        self,
        retrieved_docs: List[Dict[str, Any]],
        relevant_docs: List[str],
        k: int = None
    ) -> Dict[str, float]:
        """Calculate comprehensive retrieval metrics"""
        if not retrieved_docs or not relevant_docs:
            return {
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "ndcg": 0.0,
                "mrr": 0.0
            }
            
        # Convert retrieved docs to list of IDs
        retrieved_ids = [doc['document'].metadata['doc_id'] for doc in retrieved_docs[:k] if doc['score'] > 0.5]
        relevant_ids = set(relevant_docs)
        
        print("\n[Metrics Debug] Retrieval Analysis:")
        print(f"Retrieved documents: {retrieved_ids}")
        print(f"Relevant documents: {relevant_ids}")
        print(f"Number of retrieved: {len(retrieved_ids)}")
        print(f"Number of relevant: {len(relevant_ids)}")
        
        # Calculate basic metrics
        true_positives = len(set(retrieved_ids) & relevant_ids)
        precision = true_positives / len(retrieved_ids) if retrieved_ids else 0
        recall = true_positives / len(relevant_ids) if relevant_ids else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"True positives: {true_positives}")
        print(f"Precision: {precision:.3f}")
        print(f"Recall: {recall:.3f}")
        print(f"F1: {f1:.3f}")
        
        # Calculate NDCG
        dcg = 0
        idcg = 0
        
        # Calculate DCG with position-aware weighting
        print("\nNDCG Calculation:")
        for i, doc_id in enumerate(retrieved_ids):
            rel = 1 if doc_id in relevant_ids else 0
            gain = (2**rel - 1) / np.log2(i + 2)
            dcg += gain
            print(f"Position {i+1}: doc_id={doc_id}, relevant={rel}, gain={gain:.3f}")
        
        # Calculate ideal DCG using all relevant documents
        print("\nIDCG Calculation:")
        ideal_rels = sorted([1 for _ in range(len(relevant_ids))], reverse=True)
        for i, rel in enumerate(ideal_rels):
            gain = (2**rel - 1) / np.log2(i + 2)
            idcg += gain
            print(f"Position {i+1}: relevance={rel}, gain={gain:.3f}")
            
        ndcg = dcg / idcg if idcg > 0 else 0
        print(f"\nFinal NDCG: DCG={dcg:.3f}, IDCG={idcg:.3f}, NDCG={ndcg:.3f}")
        
        # Calculate MRR - handle no relevant docs case
        mrr = 0
        if relevant_ids:
            print("\nMRR Calculation:")
            ranks = []
            for i, doc_id in enumerate(retrieved_ids):
                if doc_id in relevant_ids:
                    rank = 1 / (i + 1)
                    ranks.append(rank)
                    print(f"Position {i+1}: doc_id={doc_id}, relevant=True, rank={rank:.3f}")
                else:
                    print(f"Position {i+1}: doc_id={doc_id}, relevant=False")
            
            mrr = max(ranks) if ranks else 0
            print(f"Final MRR: {mrr:.3f} (best rank found)")
                
        # Update metrics
        self.metrics["retrieval_precision"].append(precision)
        self.metrics["retrieval_recall"].append(recall)
        self.metrics["f1_score"].append(f1)
        self.metrics["ndcg"].append(ndcg)
        self.metrics["mrr"].append(mrr)
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "ndcg": ndcg,
            "mrr": mrr
        }
        
    def _tokenize_text(self, text: str) -> str:
        """Simple but effective tokenization"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Split on word boundaries, keeping only alphanumeric and basic punctuation
        tokens = re.findall(r'\b\w+\b|[.,!?;]', text.lower())
        return ' '.join(tokens)
    
    def calculate_answer_metrics(
        self,
        predicted_answer: str,
        ground_truth: str,
        embeddings
    ) -> Dict[str, float]:
        """Calculate comprehensive answer evaluation metrics"""
        # Track tokens
        answer_tokens = len(self.tokenizer.encode(predicted_answer))
        self.metrics["total_tokens"] += answer_tokens
        
        # Exact match - more lenient by removing punctuation and extra spaces
        pred_clean = self._tokenize_text(predicted_answer)
        truth_clean = self._tokenize_text(ground_truth)
        exact_match = 1.0 if pred_clean == truth_clean else 0.0
        
        # Cosine similarity using embeddings
        pred_emb = embeddings.embed_query(predicted_answer)
        truth_emb = embeddings.embed_query(ground_truth)
        cos_sim = float(cosine_similarity([pred_emb], [truth_emb])[0][0])
        
        try:
            # ROUGE scores with better tokenization
            rouge_scores = self.rouge_scorer.score(
                self._tokenize_text(predicted_answer),
                self._tokenize_text(ground_truth)
            )
        except Exception as e:
            print(f"[Metrics] Warning: ROUGE scoring failed: {str(e)}")
            rouge_scores = {
                "rouge1": type('obj', (object,), {"fmeasure": 0.0})(),
                "rouge2": type('obj', (object,), {"fmeasure": 0.0})(),
                "rougeL": type('obj', (object,), {"fmeasure": 0.0})()
            }
        
        # Calculate answer accuracy based on multiple factors
        semantic_match = cos_sim > 0.8
        rouge_match = rouge_scores["rouge1"].fmeasure > 0.5
        answer_accuracy = 1.0 if (semantic_match or rouge_match) else 0.0
        
        # Update metrics
        self.metrics["answer_accuracy"].append(answer_accuracy)
        self.metrics["exact_match"].append(exact_match)
        self.metrics["cosine_similarity"].append(cos_sim)
        self.metrics["rouge_scores"]["rouge1"].append(rouge_scores["rouge1"].fmeasure)
        self.metrics["rouge_scores"]["rouge2"].append(rouge_scores["rouge2"].fmeasure)
        self.metrics["rouge_scores"]["rougeL"].append(rouge_scores["rougeL"].fmeasure)
        
        return {
            "answer_accuracy": answer_accuracy,
            "exact_match": exact_match,
            "cosine_similarity": cos_sim,
            "rouge1": rouge_scores["rouge1"].fmeasure,
            "rouge2": rouge_scores["rouge2"].fmeasure,
            "rougeL": rouge_scores["rougeL"].fmeasure
        }
        
    def calculate_rouge_with_context(
        self,
        answer: str,
        context: str
    ) -> Dict[str, float]:
        """Calculate ROUGE scores against context"""
        try:
            # Tokenize both texts
            answer_tokens = self._tokenize_text(answer)
            context_tokens = self._tokenize_text(context)
            
            # Calculate ROUGE scores
            rouge_scores = self.rouge_scorer.score(answer_tokens, context_tokens)
        except Exception as e:
            print(f"[Metrics] Warning: ROUGE scoring failed: {str(e)}")
            rouge_scores = {
                "rouge1": type('obj', (object,), {"fmeasure": 0.0})(),
                "rouge2": type('obj', (object,), {"fmeasure": 0.0})(),
                "rougeL": type('obj', (object,), {"fmeasure": 0.0})()
            }
        
        # Update metrics
        self.metrics["rouge_scores"]["rouge1"].append(rouge_scores["rouge1"].fmeasure)
        self.metrics["rouge_scores"]["rouge2"].append(rouge_scores["rouge2"].fmeasure)
        self.metrics["rouge_scores"]["rougeL"].append(rouge_scores["rougeL"].fmeasure)
        
        return {
            "rouge1": rouge_scores["rouge1"].fmeasure,
            "rouge2": rouge_scores["rouge2"].fmeasure,
            "rougeL": rouge_scores["rougeL"].fmeasure
        }
        
    def track_response_time(self, start_time: datetime) -> float:
        """Calculate and track response latency"""
        latency = (datetime.now() - start_time).total_seconds()
        self.metrics["response_latency"].append(latency)
        return latency
        
    def calculate_context_retention(
        self,
        current_answer: str,
        conversation_history: List[str],
        embeddings
    ) -> float:
        """Calculate how well the answer maintains conversation context"""
        if not conversation_history:
            return 1.0
            
        # Get embeddings
        current_emb = embeddings.embed_query(current_answer)
        history_emb = embeddings.embed_query(" ".join(conversation_history[-3:]))  # Last 3 turns
        
        # Calculate similarity
        retention = float(cosine_similarity([current_emb], [history_emb])[0][0])
        self.metrics["context_retention"].append(retention)
        return retention
        
    def track_tokens(self, text: str) -> int:
        """Track tokens for a given text"""
        tokens = len(self.tokenizer.encode(text))
        self.metrics["total_tokens"] += tokens
        return tokens

    def get_aggregate_metrics(self) -> Dict[str, float]:
        """Get aggregated metrics"""
        # Helper function to safely calculate mean
        def safe_mean(values):
            return float(np.mean(values)) if values else 0.0

        # Get ROUGE scores
        rouge1 = safe_mean(self.metrics["rouge_scores"]["rouge1"])
        rouge2 = safe_mean(self.metrics["rouge_scores"]["rouge2"])
        rougeL = safe_mean(self.metrics["rouge_scores"]["rougeL"])
        
        # Get context retention
        context_retention = safe_mean(self.metrics["context_retention"])
        
        return {
            # Answer metrics
            "answer_accuracy": safe_mean(self.metrics["answer_accuracy"]),
            "exact_match_rate": safe_mean(self.metrics["exact_match"]),
            "cosine_similarity": safe_mean(self.metrics["cosine_similarity"]),
            "rouge1": rouge1,
            "rouge2": rouge2,
            "rougeL": rougeL,
            
            # Retrieval metrics
            "retrieval_precision": safe_mean(self.metrics["retrieval_precision"]),
            "retrieval_recall": safe_mean(self.metrics["retrieval_recall"]),
            "f1_score": safe_mean(self.metrics["f1_score"]),
            "ndcg": safe_mean(self.metrics["ndcg"]),
            "mrr": safe_mean(self.metrics["mrr"]),
            
            # System metrics
            "response_latency": safe_mean(self.metrics["response_latency"]),
            "context_retention": context_retention,
            "total_questions": self.metrics["total_questions"],
            "successful_retrievals": self.metrics["successful_retrievals"],
            "total_tokens": self.metrics["total_tokens"],
            "total_conversations": self.metrics["total_conversations"]
        } 