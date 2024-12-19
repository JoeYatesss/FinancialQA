from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Document(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]

class QuestionRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AnswerResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    conversation_id: Optional[str] = None

class MetricsResponse(BaseModel):
    answer_accuracy: float
    retrieval_precision: float
    response_latency: float
    context_retention: float 