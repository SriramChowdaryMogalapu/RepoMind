# backend/app/retrieval/base.py
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    chunk_id: UUID
    repository_id: UUID
    file_id: UUID
    file_path: str
    language: str | None = None
    content: str
    start_line: int
    end_line: int
    symbol_name: str | None = None
    symbol_type: str | None = None
    parent_symbol: str | None = None
    score: float
    retrieval_method: str = "vector"  # "vector", "keyword", "hybrid"
    metadata: dict[str, Any] = {}


class BaseRetriever(ABC):
    @abstractmethod
    async def retrieve(
        self, repository_id: UUID, query: str, top_k: int = 8, path_filter: str | None = None
    ) -> list[RetrievedChunk]:
        """Retrieve top relevant code chunks for a given query and repository."""
