# backend/app/schemas/chunk.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class CodeChunkBase(BaseModel):
    repository_id: UUID
    file_id: UUID
    content: str
    start_line: int
    end_line: int
    symbol_name: Optional[str] = None
    symbol_type: Optional[str] = None
    parent_symbol: Optional[str] = None
    chunk_metadata: Optional[Dict[str, Any]] = None


class CodeChunkCreate(CodeChunkBase):
    embedding: Optional[List[float]] = None


class CodeChunkResponse(CodeChunkBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CodeChunkListResponse(BaseModel):
    repository_id: UUID
    total: int
    chunks: List[CodeChunkResponse]