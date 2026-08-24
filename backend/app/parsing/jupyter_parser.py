# backend/app/parsing/jupyter_parser.py
import json
import logging
from typing import List
from app.parsing.base import RawChunk
from app.parsing.python_ast_parser import parse_python_ast

logger = logging.getLogger(__name__)


def parse_jupyter_notebook(raw_json_str: str) -> List[RawChunk]:
    """
    Parses a .ipynb JSON document:
    1. Extracts code cells and runs Python AST parsing per cell.
    2. Extracts markdown explanation cells as doc chunks.
    3. Strips execution counters, base64 images, and stream output blobs.
    """
    chunks: List[RawChunk] = []
    
    try:
        data = json.loads(raw_json_str)
    except json.JSONDecodeError as exc:
        logger.warning(f"Malformed Jupyter notebook JSON: {exc}. Falling back to text.")
        return [RawChunk(content=raw_json_str[:1500], start_line=1, end_line=1, symbol_type="notebook")]

    cells = data.get("cells", [])
    current_line = 1

    for idx, cell in enumerate(cells):
        cell_type = cell.get("cell_type", "code")
        source = cell.get("source", "")
        
        # Source can be a string or list of lines
        if isinstance(source, list):
            cell_text = "".join(source)
        else:
            cell_text = str(source)

        if not cell_text.strip():
            continue

        num_lines = cell_text.count("\n") + 1
        end_line = current_line + num_lines - 1

        if cell_type == "code":
            # Attempt AST parse on the Python snippet
            try:
                cell_chunks = parse_python_ast(cell_text)
                for chunk in cell_chunks:
                    # Offset lines to global notebook cell line position
                    chunk.start_line += current_line - 1
                    chunk.end_line += current_line - 1
                    chunk.parent_symbol = f"Cell[{idx + 1}:code]"
                    chunks.append(chunk)
            except Exception:
                chunks.append(
                    RawChunk(
                        content=cell_text,
                        start_line=current_line,
                        end_line=end_line,
                        symbol_name=f"Cell_{idx + 1}",
                        symbol_type="notebook_code_cell"
                    )
                )
        elif cell_type == "markdown":
            chunks.append(
                RawChunk(
                    content=cell_text,
                    start_line=current_line,
                    end_line=end_line,
                    symbol_name=f"Cell_{idx + 1}_docs",
                    symbol_type="notebook_markdown_cell"
                )
            )

        current_line = end_line + 1

    return chunks