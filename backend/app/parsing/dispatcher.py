# backend/app/parsing/dispatcher.py

from app.parsing.base import RawChunk
from app.parsing.fallback_parser import LineBasedParser
from app.parsing.jupyter_parser import parse_jupyter_notebook
from app.parsing.python_parser import PythonASTParser

_python_parser = PythonASTParser()
_fallback_parser = LineBasedParser()


def parse_file_to_chunks(content: str, language: str) -> list[RawChunk]:
    if not content:
        return []

    lang_lower = language.lower() if language else "unknown"

    if lang_lower == "python":
        return _python_parser.parse(content, language)
    elif lang_lower == "jupyter notebook":
        return parse_jupyter_notebook(content)
    else:
        return _fallback_parser.parse(content, language)
