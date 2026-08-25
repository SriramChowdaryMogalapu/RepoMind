# backend/app/schemas/chat.py
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    top_k: int = Field(default=6, ge=1, le=20)
    tagged_files: Optional[List[str]] = Field(
        default=None,
        description="List of file paths explicitly pinned by the user for context injection (e.g. ['src/main.py'])"
    )


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