# backend/app/parsing/base.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod


class RawChunk(BaseModel):
    content: str
    start_line: int
    end_line: int
    symbol_name: Optional[str] = None
    symbol_type: Optional[str] = None  # function, class, method, block, module
    parent_symbol: Optional[str] = None
    language: str
    metadata: Dict[str, Any] = {}


class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: str, language: str) -> List[RawChunk]:
        """Parses source code content into structured code chunks."""
        pass