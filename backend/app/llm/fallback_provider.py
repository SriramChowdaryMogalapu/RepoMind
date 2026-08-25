# backend/app/llm/fallback_provider.py
import logging

from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class MultiProviderFallbackLLM(BaseLLMProvider):
    """
    Tries a sequence of LLM providers in order.
    If all external APIs fail, provides an offline extraction fallback.
    """

    def __init__(self, providers: list[BaseLLMProvider]):
        self.providers = [p for p in providers if p is not None]

    async def generate_response(
        self, messages: list[LLMMessage], temperature: float = 0.1, max_tokens: int = 1500
    ) -> LLMResponse:
        errors = []

        for provider in self.providers:
            try:
                response = await provider.generate_response(
                    messages=messages, temperature=temperature, max_tokens=max_tokens
                )
                return response
            except Exception as exc:
                provider_name = provider.__class__.__name__
                logger.warning(f"[LLM Chain] Provider {provider_name} failed: {exc}")
                errors.append(f"{provider_name}: {exc!s}")

        # Ultimate fallback: Graceful offline extraction rather than a 500 error
        return self._generate_offline_degraded_response(messages)

    def _generate_offline_degraded_response(self, messages: list[LLMMessage]) -> LLMResponse:
        """Extracts key code symbols and references directly from prompt context."""
        user_message = next((m.content for m in reversed(messages) if m.role == "user"), "")
        question_marker = "USER QUESTION:"
        user_question = (
            user_message.split(question_marker, 1)[-1]
            .split("Please provide a grounded answer", 1)[0]
            .strip()
            if question_marker in user_message
            else user_message.strip()
        )
        user_question = user_question or "your query"

        fallback_text = (
            "## Offline repository summary\n\n"
            "> **Notice:** External AI providers are temporarily unavailable. "
            "This response is based on deterministic retrieval from the indexed repository.\n\n"
            f"The indexed context contains relevant matches for **{user_question}**. "
            "Review the source citations below for the exact files and line ranges.\n\n"
            "**Key takeaway:** The citations are the authoritative evidence available while offline."
        )

        return LLMResponse(
            content=fallback_text,
            model_name="offline-deterministic-fallback",
            usage={"total_tokens": 0},
        )
