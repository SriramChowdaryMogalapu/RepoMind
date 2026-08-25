# backend/app/embeddings/fastembed_provider.py
import asyncio

from app.embeddings.base import EmbeddingProvider


class FastEmbedProvider(EmbeddingProvider):
    """
    Local embeddings using FastEmbed (ONNX runtime, CPU-optimized, zero API cost).
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        from fastembed import TextEmbedding

        self.model_name = model_name
        self.model = TextEmbedding(model_name=model_name)
        # Default dimension for bge-small-en-v1.5 is 384
        self._dim = 384 if "small" in model_name else 768

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_text(self, text: str) -> list[float]:
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, lambda: list(self.model.embed([text])))
        return embeddings[0].tolist()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: [e.tolist() for e in self.model.embed(texts)]
        )
        return embeddings
