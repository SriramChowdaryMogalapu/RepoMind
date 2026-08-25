# backend/app/llm/factory.py
from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.fallback_provider import MultiProviderFallbackLLM
from app.llm.mock_provider import MockLLMProvider


def _is_valid_key(key: str | None) -> bool:
    """Checks that a key exists, is non-empty, and is not a placeholder."""
    if not key:
        return False
    k = key.strip()
    return bool(k) and not k.startswith("your_") and not k.startswith("sk-proj-your")


def get_llm_provider() -> BaseLLMProvider:
    providers = []

    # 1. Check Gemini: Add only if key exists and provider matches
    if settings.LLM_PROVIDER == "gemini" and _is_valid_key(settings.LLM_API_KEY):
        from app.llm.gemini_provider import GeminiLLMProvider

        providers.append(
            GeminiLLMProvider(
                api_key=settings.LLM_API_KEY.strip(),
                model_name=settings.LLM_MODEL or "gemini-1.5-flash",
                base_url=settings.LLM_BASE_URL,
            )
        )

    # 2. Check OpenAI / Secondary Cloud: Add only if OpenAI key is present
    if _is_valid_key(settings.OPENAI_API_KEY):
        from app.llm.openai_provider import OpenAILLMProvider

        providers.append(
            OpenAILLMProvider(
                api_key=settings.OPENAI_API_KEY.strip(),
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            )
        )

    # 3. Check generic LLM_API_KEY for custom OpenAI-compatible endpoints (Groq, OpenRouter)
    if settings.LLM_PROVIDER in {"openai", "groq", "openrouter"} and _is_valid_key(
        settings.LLM_API_KEY
    ):
        from app.llm.openai_provider import OpenAILLMProvider

        # Avoid duplicate if already registered via OPENAI_API_KEY
        if not any(isinstance(p, OpenAILLMProvider) for p in providers):
            providers.append(
                OpenAILLMProvider(
                    api_key=settings.LLM_API_KEY.strip(),
                    model_name=settings.LLM_MODEL or "gpt-4o-mini",
                    base_url=getattr(settings, "LLM_BASE_URL", "https://api.openai.com/v1"),
                )
            )

    # 4. Fallback: If no provider keys are configured, use local MockLLMProvider
    if not providers:
        providers.append(MockLLMProvider())

    return MultiProviderFallbackLLM(providers=providers)
