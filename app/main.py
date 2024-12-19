from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json
from datetime import datetime

from app.rag.engine import RAGEngine

app = FastAPI(title="Financial RAG System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine
rag_engine = RAGEngine()

class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    answer: str
    context: str
    metrics: Dict[str, Any]
    search_results: List[Dict[str, Any]]

@app.post("/api/question", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that processes questions using the RAG system
    """
    try:
        response = await rag_engine.process_question(
            question=request.question,
            conversation_id=request.conversation_id,
            context=request.context
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics():
    """
    Get metrics for all conversations
    """
    try:
        metrics_data = rag_engine.get_metrics()
        return {
            "status": "success",
            "metrics": metrics_data["metrics"],
            "history": metrics_data["history"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/{conversation_id}")
async def get_conversation_metrics(conversation_id: str):
    """
    Get metrics for a specific conversation
    """
    try:
        metrics = rag_engine.get_metrics(conversation_id)
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 