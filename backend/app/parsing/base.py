# backend/app/parsing/base.py
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class RawChunk(BaseModel):
    content: str
    start_line: int
    end_line: int
    symbol_name: str | None = None
    symbol_type: str | None = None  # function, class, method, block, module
    parent_symbol: str | None = None
    language: str
    metadata: dict[str, Any] = {}


class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: str, language: str) -> list[RawChunk]:
        """Parses source code content into structured code chunks."""
