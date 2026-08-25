# backend/app/embeddings/openai_provider.py
import httpx
from fastapi import status

from app.core.errors import AppException
from app.embeddings.base import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    Cloud embeddings using OpenAI or OpenAI-compatible embedding APIs.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "text-embedding-3-small",
        base_url: str = "https://api.openai.com/v1",
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self._dim = 1536

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_text(self, text: str) -> list[float]:
        results = await self.embed_batch([text])
        return results[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        # Sanitize empty strings to prevent API rejection
        cleaned = [t if t.strip() else " " for t in texts]

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model_name, "input": cleaned}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/embeddings", headers=headers, json=payload)
            if resp.status_code != 200:
                raise AppException(
                    code="EMBEDDING_API_ERROR",
                    message=f"Embedding API error: {resp.text}",
                    status_code=status.HTTP_502_BAD_GATEWAY,
                )
            data = resp.json()
            # Sort by index to ensure proper sequence
            items = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in items]
