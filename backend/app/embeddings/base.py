# backend/app/embeddings/base.py
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """
    Abstract Base Class for all embedding generation providers.
    Enables switching between local, OpenAI, Gemini, or mock providers without codebase changes.
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the vector dimensionality produced by this model."""

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector for a single string."""

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of strings."""
