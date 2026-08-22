# backend/app/retrieval/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    chunk_id: UUID
    repository_id: UUID
    file_id: UUID
    file_path: str
    language: Optional[str] = None
    content: str
    start_line: int
    end_line: int
    symbol_name: Optional[str] = None
    symbol_type: Optional[str] = None
    parent_symbol: Optional[str] = None
    score: float
    retrieval_method: str = "vector"  # "vector", "keyword", "hybrid"
    metadata: Dict[str, Any] = {}


class BaseRetriever(ABC):
    @abstractmethod
    async def retrieve(
        self,
        repository_id: UUID,
        query: str,
        top_k: int = 8,
        path_filter: Optional[str] = None
    ) -> List[RetrievedChunk]:
        """Retrieve top relevant code chunks for a given query and repository."""
        pass