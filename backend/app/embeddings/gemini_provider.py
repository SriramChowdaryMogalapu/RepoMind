# backend/app/embeddings/gemini_provider.py

import httpx
from fastapi import status

from app.core.errors import AppException
from app.embeddings.base import EmbeddingProvider


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-embedding-001",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    ):
        self.api_key = api_key
        self.model_name = model_name.replace("models/", "")
        self.base_url = base_url.rstrip("/")
        self._dim = 1536  # Matches pgvector column dimension

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_text(self, text: str) -> list[float]:
        results = await self.embed_batch([text])
        return results[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        url = f"{self.base_url}/models/{self.model_name}:batchEmbedContents?key={self.api_key}"

        requests_payload = [
            {
                "model": f"models/{self.model_name}",
                "content": {"parts": [{"text": t if t.strip() else " "}]},
                "outputDimensionality": 1536,
            }
            for t in texts
        ]

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json={"requests": requests_payload})
            if resp.status_code != 200:
                raise AppException(
                    code="GEMINI_EMBEDDING_ERROR",
                    message=f"Gemini embedding API error: {resp.text}",
                    status_code=status.HTTP_502_BAD_GATEWAY,
                )
            data = resp.json()
            embeddings = [item["values"] for item in data.get("embeddings", [])]
            return embeddings
