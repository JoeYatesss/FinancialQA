import json
import os
from typing import Dict, Any
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import print as rprint

class MetricsStorage:
    def __init__(self, storage_path: str = "data/metrics"):
        """Initialize metrics storage"""
        self.storage_path = storage_path
        self.metrics_file = os.path.join(storage_path, "metrics.json")
        self.console = Console()
        
        # Force reset metrics on initialization
        print("\n[Metrics Storage] Initializing with fresh metrics...")
        self._reset_metrics()
        
    def _reset_metrics(self):
        """Reset metrics file to initial state"""
        os.makedirs(self.storage_path, exist_ok=True)
        initial_metrics = {
            "metrics_history": [],
            "aggregate_metrics": {
                "answer_accuracy": 0.0,
                "exact_match_rate": 0.0,
                "cosine_similarity": 0.0,
                "rouge1": 0.0,
                "rouge2": 0.0,
                "rougeL": 0.0,
                "retrieval_precision": 0.0,
                "retrieval_recall": 0.0,
                "f1_score": 0.0,
                "ndcg": 0.0,
                "mrr": 0.0,
                "response_latency": 0.0,
                "context_retention": 0.0,
                "total_questions": 0,
                "successful_retrievals": 0,
                "total_conversations": 0,
                "total_tokens": 0
            }
        }
        self._save_metrics(initial_metrics)
        print("[Metrics Storage] Metrics reset complete\n")
    
    def _ensure_storage_exists(self):
        """Ensure storage directory and files exist"""
        os.makedirs(self.storage_path, exist_ok=True)
        if not os.path.exists(self.metrics_file):
            self._reset_metrics()
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load metrics from storage"""
        try:
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metrics: {str(e)}")
            return {
                "metrics_history": [],
                "aggregate_metrics": {}
            }
    
    def _save_metrics(self, metrics_data: Dict[str, Any]):
        """Save metrics to storage"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {str(e)}")
    
    def _print_metrics(self, metrics: Dict[str, Any]):
        """Print metrics to terminal in a formatted table"""
        # Create a table for answer quality metrics
        answer_table = Table(title="Answer Quality Metrics", show_header=True)
        answer_table.add_column("Metric", style="cyan")
        answer_table.add_column("Value", style="magenta")
        
        answer_metrics = [
            ("Answer Accuracy", metrics.get("answer_accuracy", 0)),
            ("Exact Match Rate", metrics.get("exact_match_rate", 0)),
            ("Cosine Similarity", metrics.get("cosine_similarity", 0)),
            ("ROUGE-1", metrics.get("rouge1", 0)),
            ("ROUGE-2", metrics.get("rouge2", 0)),
            ("ROUGE-L", metrics.get("rougeL", 0))
        ]
        
        for name, value in answer_metrics:
            answer_table.add_row(name, f"{value:.2%}")
            
        # Create a table for retrieval metrics
        retrieval_table = Table(title="Retrieval Metrics", show_header=True)
        retrieval_table.add_column("Metric", style="cyan")
        retrieval_table.add_column("Value", style="magenta")
        
        retrieval_metrics = [
            ("Precision", metrics.get("retrieval_precision", 0)),
            ("Recall", metrics.get("retrieval_recall", 0)),
            ("F1 Score", metrics.get("f1_score", 0)),
            ("NDCG", metrics.get("ndcg", 0)),
            ("MRR", metrics.get("mrr", 0))
        ]
        
        for name, value in retrieval_metrics:
            retrieval_table.add_row(name, f"{value:.2%}")
            
        # Create a table for system metrics
        system_table = Table(title="System Metrics", show_header=True)
        system_table.add_column("Metric", style="cyan")
        system_table.add_column("Value", style="magenta")
        
        system_metrics = [
            ("Response Latency", f"{metrics.get('response_latency', 0):.2f}s"),
            ("Context Retention", f"{metrics.get('context_retention', 0):.2%}"),
            ("Total Questions", str(metrics.get("total_questions", 0))),
            ("Successful Retrievals", str(metrics.get("successful_retrievals", 0))),
            ("Total Conversations", str(metrics.get("total_conversations", 0))),
            ("Total Tokens", str(metrics.get("total_tokens", 0)))
        ]
        
        for name, value in system_metrics:
            system_table.add_row(name, value)
        
        # Print timestamp and tables
        self.console.print(f"\n[bold green]Metrics Update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold green]")
        self.console.print(answer_table)
        self.console.print(retrieval_table)
        self.console.print(system_table)
        self.console.print("\n")
    
    def update_metrics(self, new_metrics: Dict[str, Any]):
        """Update stored metrics with new values"""
        print("\n[Metrics Storage] Updating metrics...")
        metrics_data = self._load_metrics()
        
        # Add metrics to history with timestamp
        metrics_with_timestamp = {
            "timestamp": datetime.now().isoformat(),
            **new_metrics
        }
        
        # Only add to history if metrics have changed
        if not metrics_data["metrics_history"] or new_metrics != metrics_data["aggregate_metrics"]:
            metrics_data["metrics_history"].append(metrics_with_timestamp)
            # Keep only last 100 entries to prevent file from growing too large
            metrics_data["metrics_history"] = metrics_data["metrics_history"][-100:]
            
            # Update aggregate metrics
            metrics_data["aggregate_metrics"] = new_metrics
            
            # Print metrics to terminal
            print("[Metrics Storage] New metrics detected, displaying update:")
            self._print_metrics(new_metrics)
            
            # Save metrics to file
            print("[Metrics Storage] Saving to:", self.metrics_file)
            self._save_metrics(metrics_data)
            print("[Metrics Storage] Save complete\n")
        else:
            print("[Metrics Storage] No changes in metrics, skipping update\n")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get stored metrics"""
        metrics_data = self._load_metrics()
        return {
            "metrics": metrics_data["aggregate_metrics"],
            "history": metrics_data["metrics_history"]
        } 