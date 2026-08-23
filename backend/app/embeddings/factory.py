# backend/app/embeddings/factory.py
from app.embeddings.base import EmbeddingProvider
from app.embeddings.mock_provider import MockEmbeddingProvider
from app.core.config import settings


def get_embedding_provider() -> EmbeddingProvider:
    provider_type = (settings.EMBEDDING_PROVIDER or "mock").lower()

    if provider_type == "mock":
        return MockEmbeddingProvider(dimension=1536)
    elif provider_type == "gemini":
        from app.embeddings.gemini_provider import GeminiEmbeddingProvider
        api_key = settings.LLM_API_KEY or settings.OPENAI_API_KEY
        model_name = settings.EMBEDDING_MODEL or "gemini-embedding-001"
        base_url = settings.LLM_BASE_URL or "https://generativelanguage.googleapis.com/v1beta"
        return GeminiEmbeddingProvider(api_key=api_key, model_name=model_name, base_url=base_url)
    elif provider_type == "fastembed":
        from app.embeddings.fastembed_provider import FastEmbedProvider
        return FastEmbedProvider(model_name=settings.EMBEDDING_MODEL)
    elif provider_type in {"openai", "cloud"}:
        from app.embeddings.openai_provider import OpenAIEmbeddingProvider
        api_key = settings.LLM_API_KEY or settings.OPENAI_API_KEY
        return OpenAIEmbeddingProvider(api_key=api_key, model_name=settings.EMBEDDING_MODEL)
    else:
        return MockEmbeddingProvider(dimension=1536)