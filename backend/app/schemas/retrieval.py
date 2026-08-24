# backend/app/schemas/retrieval.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID


class RetrievalQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, example="Where is the database connection created?")
    top_k: int = Field(default=8, ge=1, le=20)
    path_filter: Optional[str] = None


class RetrievedChunkResponse(BaseModel):
    chunk_id: UUID
    file_path: str
    language: Optional[str] = None
    content: str
    start_line: int
    end_line: int
    symbol_name: Optional[str] = None
    symbol_type: Optional[str] = None
    parent_symbol: Optional[str] = None
    score: float
    retrieval_method: str
    metadata: Dict[str, Any] = {}


class RetrievalResponse(BaseModel):
    repository_id: UUID
    query: str
    total_candidates: int
    results: List[RetrievedChunkResponse]

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    top_k: int = Field(default=6, ge=1, le=20)
    tagged_files: Optional[List[str]] = Field(
        default=None,
        description="Explicitly tagged file paths to force into prompt context (e.g. ['src/auth/jwt.py'])"
    )