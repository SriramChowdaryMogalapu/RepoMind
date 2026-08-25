# backend/app/schemas/retrieval.py
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RetrievalQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, example="Where is the database connection created?")
    top_k: int = Field(default=8, ge=1, le=20)
    path_filter: str | None = None


class RetrievedChunkResponse(BaseModel):
    chunk_id: UUID
    file_path: str
    language: str | None = None
    content: str
    start_line: int
    end_line: int
    symbol_name: str | None = None
    symbol_type: str | None = None
    parent_symbol: str | None = None
    score: float
    retrieval_method: str
    metadata: dict[str, Any] = {}


class RetrievalResponse(BaseModel):
    repository_id: UUID
    query: str
    total_candidates: int
    results: list[RetrievedChunkResponse]


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    top_k: int = Field(default=6, ge=1, le=20)
    tagged_files: list[str] | None = Field(
        default=None,
        description="Explicitly tagged file paths to force into prompt context (e.g. ['src/auth/jwt.py'])",
    )
