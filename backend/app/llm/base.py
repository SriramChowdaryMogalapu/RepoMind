# backend/app/llm/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class LLMMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str


class LLMResponse(BaseModel):
    content: str
    model_name: str
    usage: Dict[str, Any] = {}


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 1500
    ) -> LLMResponse:
        """Generates an answer from the underlying LLM provider."""
        pass