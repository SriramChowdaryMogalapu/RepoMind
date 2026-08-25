# backend/app/schemas/chunk.py
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class CodeChunkBase(BaseModel):
    repository_id: UUID
    file_id: UUID
    content: str
    start_line: int
    end_line: int
    symbol_name: str | None = None
    symbol_type: str | None = None
    parent_symbol: str | None = None
    chunk_metadata: dict[str, Any] | None = None


class CodeChunkCreate(CodeChunkBase):
    embedding: list[float] | None = None


class CodeChunkResponse(CodeChunkBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CodeChunkListResponse(BaseModel):
    repository_id: UUID
    total: int
    chunks: list[CodeChunkResponse]
