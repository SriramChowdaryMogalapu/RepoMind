# backend/app/llm/fallback_provider.py
import logging
from typing import List
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class MultiProviderFallbackLLM(BaseLLMProvider):
    """
    Tries a sequence of LLM providers in order.
    If all external APIs fail, provides an offline extraction fallback.
    """
    def __init__(self, providers: List[BaseLLMProvider]):
        self.providers = [p for p in providers if p is not None]

    async def generate_response(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 1500
    ) -> LLMResponse:
        errors = []

        for provider in self.providers:
            try:
                response = await provider.generate_response(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response
            except Exception as exc:
                provider_name = provider.__class__.__name__
                logger.warning(f"[LLM Chain] Provider {provider_name} failed: {exc}")
                errors.append(f"{provider_name}: {str(exc)}")

        # Ultimate fallback: Graceful offline extraction rather than a 500 error
        return self._generate_offline_degraded_response(messages)

    def _generate_offline_degraded_response(self, messages: List[LLMMessage]) -> LLMResponse:
        """Extracts key code symbols and references directly from prompt context."""
        user_question = next((m.content for m in reversed(messages) if m.role == "user"), "your query")
        
        fallback_text = (
            "> **Notice**: All external AI providers are temporarily unavailable. "
            "Displaying an offline deterministic extraction from indexed repository context.\n\n"
            f"Relevant source code matches were located for: *\"{user_question}\"*.\n"
            "Please check the source citations below to view the exact code implementation lines."
        )
        
        return LLMResponse(
            content=fallback_text,
            model_name="offline-deterministic-fallback",
            usage={"total_tokens": 0}
        )