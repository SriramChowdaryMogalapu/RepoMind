# backend/app/llm/factory.py
from app.llm.base import BaseLLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.core.config import settings


def get_llm_provider() -> BaseLLMProvider:
    provider = (settings.LLM_PROVIDER or "mock").lower()

    if provider == "mock":
        return MockLLMProvider()
    elif provider == "gemini":
        from app.llm.gemini_provider import GeminiLLMProvider
        api_key = settings.LLM_API_KEY or settings.OPENAI_API_KEY
        base_url = settings.LLM_BASE_URL or "https://generativelanguage.googleapis.com/v1beta"
        model = settings.LLM_MODEL or "gemini-1.5-flash"
        return GeminiLLMProvider(api_key=api_key, model_name=model, base_url=base_url)
    elif provider in {"openai", "openrouter", "groq"}:
        from app.llm.openai_provider import OpenAILLMProvider
        api_key = settings.LLM_API_KEY or settings.OPENAI_API_KEY
        base_url = getattr(settings, "LLM_BASE_URL", "https://api.openai.com/v1")
        model = settings.LLM_MODEL or "gpt-4o-mini"
        return OpenAILLMProvider(api_key=api_key, model_name=model, base_url=base_url)
    else:
        return MockLLMProvider()