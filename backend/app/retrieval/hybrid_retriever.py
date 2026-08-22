# backend/app/retrieval/hybrid_retriever.py
import re
from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.models.chunk import CodeChunk
from app.models.file import File
from app.retrieval.base import BaseRetriever, RetrievedChunk
from app.embeddings.factory import get_embedding_provider


class HybridRetriever(BaseRetriever):
    """
    Performs hybrid retrieval using vector cosine distance and keyword/symbol matching,
    reranked using Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_provider = get_embedding_provider()

    async def _vector_search(
        self, repository_id: UUID, query: str, limit: int, path_filter: Optional[str] = None
    ) -> List[RetrievedChunk]:
        query_vector = await self.embedding_provider.embed_text(query)

        # Cosine distance order using pgvector <=> operator
        stmt = (
            select(
                CodeChunk,
                File.path.label("file_path"),
                File.language.label("file_language"),
                CodeChunk.embedding.cosine_distance(query_vector).label("distance")
            )
            .join(File, CodeChunk.file_id == File.id)
            .where(CodeChunk.repository_id == repository_id)
        )

        if path_filter:
            stmt = stmt.where(File.path.ilike(f"%{path_filter}%"))

        stmt = stmt.order_by("distance").limit(limit)
        result = await self.db.execute(stmt)
        rows = result.all()

        candidates = []
        for chunk, file_path, file_language, distance in rows:
            # Convert cosine distance to similarity score in range [0, 1]
            similarity = max(0.0, 1.0 - float(distance or 0.0))
            candidates.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    repository_id=chunk.repository_id,
                    file_id=chunk.file_id,
                    file_path=file_path,
                    language=file_language,
                    content=chunk.content,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    symbol_name=chunk.symbol_name,
                    symbol_type=chunk.symbol_type,
                    parent_symbol=chunk.parent_symbol,
                    score=similarity,
                    retrieval_method="vector",
                    metadata=chunk.chunk_metadata or {}
                )
            )
        return candidates

    async def _keyword_search(
        self, repository_id: UUID, query: str, limit: int, path_filter: Optional[str] = None
    ) -> List[RetrievedChunk]:
        # Extract potential identifiers and alphanumeric terms
        terms = re.findall(r"[a-zA-Z0-9_\-\.]+", query)
        if not terms:
            return []

        conditions = []
        for term in terms[:5]:  # Limit query expansion terms
            conditions.append(CodeChunk.content.ilike(f"%{term}%"))
            conditions.append(CodeChunk.symbol_name.ilike(f"%{term}%"))

        stmt = (
            select(
                CodeChunk,
                File.path.label("file_path"),
                File.language.label("file_language")
            )
            .join(File, CodeChunk.file_id == File.id)
            .where(CodeChunk.repository_id == repository_id)
            .where(or_(*conditions))
        )

        if path_filter:
            stmt = stmt.where(File.path.ilike(f"%{path_filter}%"))

        stmt = stmt.limit(limit * 2)
        result = await self.db.execute(stmt)
        rows = result.all()

        candidates = []
        for chunk, file_path, file_language in rows:
            # Score based on exact identifier occurrence count
            exact_matches = sum(1 for t in terms if t.lower() in chunk.content.lower())
            symbol_bonus = 2 if chunk.symbol_name and any(t.lower() == chunk.symbol_name.lower() for t in terms) else 0
            raw_score = exact_matches + symbol_bonus

            candidates.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    repository_id=chunk.repository_id,
                    file_id=chunk.file_id,
                    file_path=file_path,
                    language=file_language,
                    content=chunk.content,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    symbol_name=chunk.symbol_name,
                    symbol_type=chunk.symbol_type,
                    parent_symbol=chunk.parent_symbol,
                    score=float(raw_score),
                    retrieval_method="keyword",
                    metadata=chunk.chunk_metadata or {}
                )
            )

        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:limit]

    async def retrieve(
        self,
        repository_id: UUID,
        query: str,
        top_k: int = 8,
        path_filter: Optional[str] = None
    ) -> List[RetrievedChunk]:
        vector_results = await self._vector_search(repository_id, query, limit=top_k * 2, path_filter=path_filter)
        keyword_results = await self._keyword_search(repository_id, query, limit=top_k * 2, path_filter=path_filter)

        # Reciprocal Rank Fusion (RRF) with constant k=60
        k = 60
        rrf_scores: Dict[UUID, float] = {}
        chunk_map: Dict[UUID, RetrievedChunk] = {}

        for rank, item in enumerate(vector_results):
            chunk_map[item.chunk_id] = item
            rrf_scores[item.chunk_id] = rrf_scores.get(item.chunk_id, 0.0) + (1.0 / (k + rank + 1))

        for rank, item in enumerate(keyword_results):
            if item.chunk_id not in chunk_map:
                chunk_map[item.chunk_id] = item
            rrf_scores[item.chunk_id] = rrf_scores.get(item.chunk_id, 0.0) + (1.0 / (k + rank + 1))

        sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        final_candidates: List[RetrievedChunk] = []
        for chunk_id, fused_score in sorted_chunks[:top_k]:
            chunk_obj = chunk_map[chunk_id]
            chunk_obj.score = fused_score
            chunk_obj.retrieval_method = "hybrid"
            final_candidates.append(chunk_obj)

        return final_candidates