# backend/app/embeddings/factory.py
from app.embeddings.base import EmbeddingProvider
from app.embeddings.mock_provider import MockEmbeddingProvider
from app.embeddings.fallback_provider import MultiProviderFallbackEmbedding
from app.core.config import settings


def _is_valid_key(key: str | None) -> bool:
    """Checks that a key exists, is non-empty, and is not a placeholder."""
    if not key:
        return False
    k = key.strip()
    return bool(k) and not k.startswith("your_") and not k.startswith("sk-proj-your")


def get_embedding_provider() -> EmbeddingProvider:
    providers = []

    # 1. Check Gemini: Add only if key exists and provider is set to gemini
    if settings.EMBEDDING_PROVIDER == "gemini" and _is_valid_key(settings.LLM_API_KEY):
        from app.embeddings.gemini_provider import GeminiEmbeddingProvider
        providers.append(
            GeminiEmbeddingProvider(
                api_key=settings.LLM_API_KEY.strip(),
                model_name=settings.EMBEDDING_MODEL or "text-embedding-004",
                base_url=settings.LLM_BASE_URL
            )
        )

    # 2. Check OpenAI: Add only if OPENAI_API_KEY is present
    if _is_valid_key(settings.OPENAI_API_KEY):
        from app.embeddings.openai_provider import OpenAIEmbeddingProvider
        providers.append(
            OpenAIEmbeddingProvider(
                api_key=settings.OPENAI_API_KEY.strip(),
                model_name="text-embedding-3-small"
            )
        )

    # 3. Check FastEmbed (local ONNX, requires no API key)
    if settings.EMBEDDING_PROVIDER == "fastembed":
        from app.embeddings.fastembed_provider import FastEmbedProvider
        providers.append(FastEmbedProvider(model_name=settings.EMBEDDING_MODEL))

    # 4. Fallback: If no cloud keys exist, use MockEmbeddingProvider (1536d)
    if not providers:
        providers.append(MockEmbeddingProvider(dimension=1536))

    return MultiProviderFallbackEmbedding(providers=providers, dimension=1536)