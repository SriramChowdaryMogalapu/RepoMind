# backend/tests/test_embeddings.py
import pytest

from app.embeddings.factory import get_embedding_provider
from app.embeddings.fallback_provider import MultiProviderFallbackEmbedding
from app.embeddings.mock_provider import MockEmbeddingProvider
from app.core.config import settings


@pytest.mark.asyncio
async def test_mock_embedding_generation():
    print("\n[TEST] Initializing MockEmbeddingProvider with 1536 dimensions...")
    provider = MockEmbeddingProvider(dimension=1536)
    assert provider.dimension == 1536
    print(f"[TEST] Provider dimension confirmed: {provider.dimension}")

    text = "def authenticate_user(token: str): return True"
    print(f"[TEST] Generating single embedding for code: '{text}'")
    emb = await provider.embed_text(text)

    assert len(emb) == 1536
    assert isinstance(emb[0], float)
    print(f"[TEST] Output vector sample (first 5 elements): {emb[:5]}")

    # Verify determinism
    emb_second = await provider.embed_text(text)
    assert emb == emb_second
    print("[TEST] Deterministic vector generation verified successfully.")


@pytest.mark.asyncio
async def test_mock_batch_embeddings():
    print("\n[TEST] Testing batch embedding generation...")
    provider = MockEmbeddingProvider(dimension=1536)
    texts = ["import os", "class DatabaseConnection:", "def query_database(sql: str): pass"]
    print(f"[TEST] Embedding batch of {len(texts)} items.")
    results = await provider.embed_batch(texts)

    assert len(results) == 3
    for idx, r in enumerate(results):
        assert len(r) == 1536
        print(f"[TEST] Batch item {idx} embedded with dimension {len(r)}")

    # Different texts must produce distinct vectors
    assert results[0] != results[1]
    assert results[1] != results[2]
    print("[TEST] Vector divergence for different inputs verified.")


def test_embedding_factory_default(monkeypatch):
    print("\n[TEST] Testing get_embedding_provider() factory resolution...")
    monkeypatch.setattr(settings, "EMBEDDING_PROVIDER", "mock")
    monkeypatch.setattr(settings, "LLM_API_KEY", None)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)
    provider = get_embedding_provider()
    assert isinstance(provider, MultiProviderFallbackEmbedding)
    assert any(isinstance(candidate, MockEmbeddingProvider) for candidate in provider.providers)
    print(f"[TEST] Factory resolved to default provider: {type(provider).__name__}")
