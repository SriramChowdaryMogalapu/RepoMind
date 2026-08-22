# backend/app/parsing/fallback_parser.py
import re
from typing import List, Optional
from app.parsing.base import BaseParser, RawChunk

# Regex patterns for common definitions in C-style languages, JS/TS, Go, Rust
SIGNATURE_PATTERNS = [
    # JS/TS functions & classes
    re.compile(r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(?P<name>[a-zA-Z0-9_$]+)", re.M),
    re.compile(r"^(?:export\s+)?(?:const|let|var)\s+(?P<name>[a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", re.M),
    re.compile(r"^(?:export\s+)?(?:abstract\s+)?class\s+(?P<name>[a-zA-Z0-9_$]+)", re.M),
    re.compile(r"^(?:export\s+)?interface\s+(?P<name>[a-zA-Z0-9_$]+)", re.M),
    # Go func
    re.compile(r"^func\s+(?:\([^)]+\)\s+)?(?P<name>[a-zA-Z0-9_]+)\s*\(", re.M),
    # Rust fn & struct/impl
    re.compile(r"^(?:pub\s+)?(?:async\s+)?fn\s+(?P<name>[a-zA-Z0-9_]+)", re.M),
    re.compile(r"^(?:pub\s+)?(?:struct|enum|trait|impl)\s+(?P<name>[a-zA-Z0-9_]+)", re.M),
]


class LineBasedParser(BaseParser):
    def __init__(self, max_lines_per_chunk: int = 50, overlap_lines: int = 10):
        self.max_lines = max_lines_per_chunk
        self.overlap = overlap_lines

    def parse(self, content: str, language: str) -> List[RawChunk]:
        if not content.strip():
            return []

        lines = content.splitlines(keepends=True)
        total_lines = len(lines)
        chunks: List[RawChunk] = []

        # If file is short enough, keep as single chunk
        if total_lines <= self.max_lines:
            return [
                RawChunk(
                    content=content,
                    start_line=1,
                    end_line=total_lines,
                    symbol_name=None,
                    symbol_type="module",
                    language=language
                )
            ]

        start_idx = 0
        while start_idx < total_lines:
            end_idx = min(start_idx + self.max_lines, total_lines)
            chunk_lines = lines[start_idx:end_idx]
            chunk_content = "".join(chunk_lines)

            # Discover top symbol if matched
            matched_symbol: Optional[str] = None
            for pattern in SIGNATURE_PATTERNS:
                m = pattern.search(chunk_content)
                if m:
                    matched_symbol = m.group("name")
                    break

            chunks.append(RawChunk(
                content=chunk_content,
                start_line=start_idx + 1,
                end_line=end_idx,
                symbol_name=matched_symbol,
                symbol_type="block" if not matched_symbol else "symbol_block",
                language=language
            ))

            if end_idx == total_lines:
                break
            start_idx += (self.max_lines - self.overlap)

        return chunks