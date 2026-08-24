# In backend/app/parsing/dispatcher.py:
from app.parsing.jupyter_parser import parse_jupyter_notebook
from app.parsing.python_ast_parser import parse_python_ast
from app.parsing.line_chunker import parse_by_line_window


def parse_file_to_chunks(content: str, language: str) -> list[RawChunk]:
    if language == "Jupyter Notebook":
        return parse_jupyter_notebook(content)
    elif language == "Python":
        try:
            return parse_python_ast(content)
        except Exception:
            return parse_by_line_window(content, language)
    else:
        return parse_by_line_window(content, language)