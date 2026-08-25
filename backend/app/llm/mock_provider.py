# backend/app/llm/mock_provider.py
import re

from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM provider for zero-cost, grounded offline tests.
    Parses context markers and constructs deterministic grounded responses.
    """

    def __init__(self, model_name: str = "mock-grounded-model"):
        self.model_name = model_name

    async def generate_response(
        self, messages: list[LLMMessage], temperature: float = 0.1, max_tokens: int = 1500
    ) -> LLMResponse:
        user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "")

        # Check for context blocks passed in prompt
        file_matches = re.findall(r"FILE:\s*([^\n]+)", user_msg)
        symbol_matches = re.findall(r"SYMBOL:\s*([^\n]+)", user_msg)

        if not file_matches:
            content = "I could not find enough evidence in the indexed repository to answer this reliably."
        else:
            files_str = ", ".join(set(file_matches))
            symbols_str = ", ".join([s for s in set(symbol_matches) if s and s != "None"])
            symbol_desc = f" focusing on symbols: `{symbols_str}`" if symbols_str else ""
            content = (
                f"Based on the repository context, the requested functionality is implemented across {files_str}{symbol_desc}. "
                "The code defines the relevant operational flow according to the extracted source blocks."
            )

        return LLMResponse(
            content=content,
            model_name=self.model_name,
            usage={"prompt_tokens": 120, "completion_tokens": 45, "total_tokens": 165},
        )
