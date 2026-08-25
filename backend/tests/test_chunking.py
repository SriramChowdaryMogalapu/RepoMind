# backend/tests/test_chunking.py
from app.parsing.dispatcher import parse_file_to_chunks


def test_python_ast_parsing():
    print("\n[TEST] Testing Python AST-aware structural chunking...")
    sample_py = """
class AuthService:
    def __init__(self, key: str):
        self.key = key

    def authenticate_user(self, username: str) -> bool:
        return username == "admin"

def standalone_helper():
    return True
"""
    chunks = parse_file_to_chunks(sample_py, "Python")
    print(f"[TEST] Parsed {len(chunks)} chunks from Python code.")
    assert len(chunks) >= 3

    symbols = {c.symbol_name: c for c in chunks if c.symbol_name}
    print(f"[TEST] Discovered symbols: {list(symbols.keys())}")

    assert "AuthService" in symbols
    assert symbols["AuthService"].symbol_type == "class"
    assert "authenticate_user" in symbols
    assert symbols["authenticate_user"].parent_symbol == "AuthService"
    assert "standalone_helper" in symbols
    print("[TEST] Structural parent-child relationships and types confirmed.")


def test_fallback_line_chunking_with_overlap():
    print("\n[TEST] Testing fallback line-based chunking with sliding overlap...")
    sample_js = "\n".join([f"const line_{i} = {i};" for i in range(120)])
    chunks = parse_file_to_chunks(sample_js, "JavaScript")

    print(f"[TEST] Generated {len(chunks)} overlapping chunks for 120 lines of JS.")
    assert len(chunks) > 1
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 50
    assert chunks[1].start_line == 41  # 50 - 10 + 1 (with 10-line overlap)
    print(f"[TEST] Chunk 0 lines: {chunks[0].start_line}-{chunks[0].end_line}")
    print(f"[TEST] Chunk 1 lines: {chunks[1].start_line}-{chunks[1].end_line}")


def test_empty_content_returns_empty():
    print("\n[TEST] Testing empty and whitespace input handling...")
    assert parse_file_to_chunks("", "Python") == []
    assert parse_file_to_chunks("   ", "TypeScript") == []
    print("[TEST] Empty input checks passed.")
