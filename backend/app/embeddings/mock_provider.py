# backend/app/embeddings/mock_provider.py
import hashlib
import math
from typing import List
from app.embeddings.base import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    """
    Generates deterministic normalized pseudo-embeddings from SHA256 hashes.
    Useful for local testing and CI/CD without API keys or heavy weights.
    """

    def __init__(self, dimension: int = 1536):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def _generate_vector(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self._dim

        # Generate seed hash
        hash_digest = hashlib.sha256(text.encode("utf-8")).digest()
        
        # Build deterministic pseudo-random float vector
        raw_vec = []
        for i in range(self._dim):
            byte_val = hash_digest[i % len(hash_digest)]
            val = ((byte_val + i * 31) % 255) / 255.0 - 0.5
            raw_vec.append(val)

        # L2-normalize vector
        norm = math.sqrt(sum(x * x for x in raw_vec))
        if norm == 0:
            return raw_vec
        return [x / norm for x in raw_vec]

    async def embed_text(self, text: str) -> List[float]:
        return self._generate_vector(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_vector(t) for t in texts]