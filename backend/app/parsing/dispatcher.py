# backend/app/parsing/dispatcher.py
from typing import List
from app.parsing.base import RawChunk
from app.parsing.python_parser import PythonASTParser
from app.parsing.fallback_parser import LineBasedParser

_python_parser = PythonASTParser()
_fallback_parser = LineBasedParser()


def parse_file_to_chunks(content: str, language: str) -> List[RawChunk]:
    if not content:
        return []

    lang_lower = language.lower() if language else "unknown"

    if lang_lower == "python":
        return _python_parser.parse(content, language)
    else:
        return _fallback_parser.parse(content, language)