# backend/app/embeddings/factory.py
from app.embeddings.base import EmbeddingProvider
from app.embeddings.mock_provider import MockEmbeddingProvider
from app.core.config import settings


def get_embedding_provider() -> EmbeddingProvider:
    provider_type = (settings.EMBEDDING_PROVIDER or "mock").lower()

    if provider_type == "mock":
        return MockEmbeddingProvider(dimension=1536)
    elif provider_type == "fastembed":
        from app.embeddings.fastembed_provider import FastEmbedProvider
        return FastEmbedProvider(model_name=getattr(settings, "EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"))
    elif provider_type in {"openai", "cloud"}:
        from app.embeddings.openai_provider import OpenAIEmbeddingProvider
        api_key = getattr(settings, "LLM_API_KEY", "") or getattr(settings, "OPENAI_API_KEY", "")
        model_name = getattr(settings, "EMBEDDING_MODEL", "text-embedding-3-small")
        return OpenAIEmbeddingProvider(api_key=api_key, model_name=model_name)
    else:
        return MockEmbeddingProvider(dimension=1536)