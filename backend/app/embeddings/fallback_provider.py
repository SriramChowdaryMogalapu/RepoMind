# backend/app/embeddings/fallback_provider.py
import logging

from app.embeddings.base import EmbeddingProvider
from app.embeddings.mock_provider import MockEmbeddingProvider

logger = logging.getLogger(__name__)


class MultiProviderFallbackEmbedding(EmbeddingProvider):
    """
    Attempts multiple embedding providers in sequence.
    Falls back to zero/deterministic vector if all remote calls fail.
    """

    def __init__(self, providers: list[EmbeddingProvider], dimension: int = 1536):
        self.providers = [p for p in providers if p is not None]
        self._dim = dimension
        self.mock_fallback = MockEmbeddingProvider(dimension=dimension)

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_text(self, text: str) -> list[float]:
        for provider in self.providers:
            try:
                return await provider.embed_text(text)
            except Exception as exc:
                logger.warning(f"[Embedding Chain] {provider.__class__.__name__} failed: {exc}")

        # When vector search APIs are down, exact keyword SQL retrieval in hybrid search still works
        return await self.mock_fallback.embed_text(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        for provider in self.providers:
            try:
                return await provider.embed_batch(texts)
            except Exception as exc:
                logger.warning(
                    f"[Embedding Batch Chain] {provider.__class__.__name__} batch failed: {exc}"
                )

        return await self.mock_fallback.embed_batch(texts)
