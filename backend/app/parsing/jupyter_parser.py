# backend/app/parsing/jupyter_parser.py

import json
import logging

from app.parsing.base import RawChunk
from app.parsing.python_parser import PythonASTParser

logger = logging.getLogger(__name__)


class JupyterNotebookParser:
    def parse(self, raw_json_str: str) -> list[RawChunk]:
        chunks: list[RawChunk] = []

        try:
            data = json.loads(raw_json_str)
        except Exception as exc:
            logger.warning(f"Malformed Jupyter notebook JSON: {exc}. Falling back to raw text.")

            return [
                RawChunk(
                    content=raw_json_str[:1500],
                    start_line=1,
                    end_line=1,
                    symbol_name=None,
                    symbol_type="notebook",
                    language="Jupyter",
                )
            ]

        cells = data.get("cells", [])
        current_line = 1

        python_parser = PythonASTParser()

        for idx, cell in enumerate(cells):
            cell_type = cell.get("cell_type", "code")
            source = cell.get("source", "")

            cell_text = "".join(source) if isinstance(source, list) else str(source)

            if not cell_text.strip():
                continue

            num_lines = cell_text.count("\n") + 1
            end_line = current_line + num_lines - 1

            if cell_type == "code":
                cell_chunks = python_parser.parse(
                    cell_text,
                    language="Python",
                )

                if cell_chunks:
                    for chunk in cell_chunks:
                        chunk.start_line += current_line - 1
                        chunk.end_line += current_line - 1

                        chunk.parent_symbol = f"Cell[{idx + 1}:code]"

                        chunk.language = "Python"

                        chunks.append(chunk)

                else:
                    chunks.append(
                        RawChunk(
                            content=cell_text,
                            start_line=current_line,
                            end_line=end_line,
                            symbol_name=f"Cell_{idx + 1}",
                            symbol_type="notebook_code_cell",
                            language="Python",
                            metadata={
                                "cell_index": idx + 1,
                                "cell_type": "code",
                            },
                        )
                    )

            elif cell_type == "markdown":
                chunks.append(
                    RawChunk(
                        content=cell_text,
                        start_line=current_line,
                        end_line=end_line,
                        symbol_name=f"Cell_{idx + 1}_docs",
                        symbol_type="notebook_markdown_cell",
                        language="Markdown",
                        metadata={
                            "cell_index": idx + 1,
                            "cell_type": "markdown",
                        },
                    )
                )

            current_line = end_line + 1

        return chunks


def parse_jupyter_notebook(raw_json_str: str) -> list[RawChunk]:
    """
    Parse a Jupyter notebook JSON string into RawChunk objects.
    """
    parser = JupyterNotebookParser()
    return parser.parse(raw_json_str)
