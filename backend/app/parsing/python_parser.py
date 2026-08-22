# backend/app/parsing/python_parser.py
import ast
from typing import List, Optional
from app.parsing.base import BaseParser, RawChunk


class PythonASTParser(BaseParser):
    def parse(self, content: str, language: str = "Python") -> List[RawChunk]:
        if not content.strip():
            return []

        lines = content.splitlines(keepends=True)
        total_lines = len(lines)

        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Fallback to line-based chunking if invalid syntax/fragment
            from app.parsing.fallback_parser import LineBasedParser
            return LineBasedParser().parse(content, language)

        chunks: List[RawChunk] = []

        def extract_code(start: int, end: int) -> str:
            return "".join(lines[start - 1:end])

        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.current_class: Optional[str] = None

            def visit_ClassDef(self, node: ast.ClassDef):
                prev_class = self.current_class
                self.current_class = node.name
                
                # Class block chunk
                start = node.lineno
                end = getattr(node, "end_lineno", node.lineno)
                code = extract_code(start, end)
                
                chunks.append(RawChunk(
                    content=code,
                    start_line=start,
                    end_line=end,
                    symbol_name=node.name,
                    symbol_type="class",
                    parent_symbol=prev_class,
                    language="Python",
                    metadata={"docstring": ast.get_docstring(node)}
                ))

                self.generic_visit(node)
                self.current_class = prev_class

            def visit_FunctionDef(self, node: ast.FunctionDef):
                self._handle_func(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
                self._handle_func(node)

            def _handle_func(self, node):
                start = node.lineno
                end = getattr(node, "end_lineno", node.lineno)
                code = extract_code(start, end)
                sym_type = "method" if self.current_class else "function"

                chunks.append(RawChunk(
                    content=code,
                    start_line=start,
                    end_line=end,
                    symbol_name=node.name,
                    symbol_type=sym_type,
                    parent_symbol=self.current_class,
                    language="Python",
                    metadata={"docstring": ast.get_docstring(node)}
                ))

        visitor = Visitor()
        visitor.visit(tree)

        # If no AST nodes (e.g. flat script, configs), create a fallback chunk
        if not chunks and content.strip():
            chunks.append(RawChunk(
                content=content,
                start_line=1,
                end_line=total_lines,
                symbol_name=None,
                symbol_type="module",
                language="Python"
            ))

        return chunks