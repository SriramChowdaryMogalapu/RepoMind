# backend/app/schemas/chat.py
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000, example="How does authentication work?")
    top_k: int = Field(default=6, ge=1, le=15)
    path_filter: Optional[str] = None


class SourceCitation(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    symbol_name: Optional[str] = None
    language: Optional[str] = None
    github_url: str


class ChatResponse(BaseModel):
    repository_id: UUID
    question: str
    answer: str
    sources: List[SourceCitation]
    confidence: str  # "high", "medium", "low", "insufficient_evidence"
    model_name: str