# backend/app/embeddings/factory.py
import logging

from app.core.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.fallback_provider import MultiProviderFallbackEmbedding
from app.embeddings.mock_provider import MockEmbeddingProvider

logger = logging.getLogger(__name__)


def _is_valid_key(key: str | None) -> bool:
    """Checks that a key exists, is non-empty, and is not a placeholder."""
    if not key:
        return False
    k = key.strip()
    return bool(k) and not k.startswith("your_") and not k.startswith("sk-proj-your")


def _model_names(value: str | list[str] | None, default: str) -> list[str]:
    """Normalize scalar/list model configuration while preserving its order."""
    names = [value] if isinstance(value, str) else value or []
    return [name.strip() for name in names if isinstance(name, str) and name.strip()] or [default]


def get_embedding_provider() -> EmbeddingProvider:
    providers = []

    # 1. Check Gemini: Add only if key exists and provider is set to gemini
    if settings.EMBEDDING_PROVIDER == "gemini" and _is_valid_key(settings.LLM_API_KEY):
        from app.embeddings.gemini_provider import GeminiEmbeddingProvider

        providers.extend(
            GeminiEmbeddingProvider(
                api_key=settings.LLM_API_KEY.strip(),
                model_name=model_name,
                base_url=settings.LLM_BASE_URL,
            )
            for model_name in _model_names(settings.EMBEDDING_MODEL, "text-embedding-004")
        )

    # 2. Check OpenAI: Add only if OPENAI_API_KEY is present
    if _is_valid_key(settings.OPENAI_API_KEY):
        from app.embeddings.openai_provider import OpenAIEmbeddingProvider

        providers.extend(
            OpenAIEmbeddingProvider(
                api_key=settings.OPENAI_API_KEY.strip(),
                model_name=model_name,
            )
            for model_name in _model_names(
                settings.EMBEDDING_MODEL if settings.EMBEDDING_PROVIDER == "openai" else None,
                "text-embedding-3-small",
            )
        )

    # 3. Check FastEmbed (local ONNX, requires no API key)
    if settings.EMBEDDING_PROVIDER == "fastembed":
        from app.embeddings.fastembed_provider import FastEmbedProvider

        for model_name in _model_names(settings.EMBEDDING_MODEL, "fast-bge-small-en-v1.5"):
            try:
                providers.append(FastEmbedProvider(model_name=model_name))
            except Exception as exc:
                logger.warning("[Embedding Chain] FastEmbed model %s unavailable: %s", model_name, exc)

    # 4. Fallback: If no cloud keys exist, use MockEmbeddingProvider (1536d)
    if not providers:
        providers.append(MockEmbeddingProvider(dimension=1536))

    return MultiProviderFallbackEmbedding(providers=providers, dimension=1536)
