# backend/app/embeddings/base.py
from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """
    Abstract Base Class for all embedding generation providers.
    Enables switching between local, OpenAI, Gemini, or mock providers without codebase changes.
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the vector dimensionality produced by this model."""
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single string."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of strings."""
        pass