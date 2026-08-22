# backend/app/llm/openai_provider.py
from typing import List
import httpx
from fastapi import status

from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.core.errors import AppException


class OpenAILLMProvider(BaseLLMProvider):
    """
    OpenAI-compatible LLM client (works with OpenAI, Groq, OpenRouter, DeepSeek).
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1"
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    async def generate_response(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 1500
    ) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            if resp.status_code != 200:
                raise AppException(
                    code="LLM_API_ERROR",
                    message=f"LLM API returned error: {resp.text}",
                    status_code=status.HTTP_502_BAD_GATEWAY
                )
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return LLMResponse(
                content=content,
                model_name=self.model_name,
                usage=usage
            )