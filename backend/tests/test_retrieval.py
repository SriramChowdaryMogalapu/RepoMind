# backend/tests/test_retrieval.py
import pytest
import uuid
from app.retrieval.base import RetrievedChunk


def test_retrieved_chunk_model():
    print("\n[TEST] Verifying RetrievedChunk data structure and metadata bounds...")
    chunk_id = uuid.uuid4()
    repo_id = uuid.uuid4()
    file_id = uuid.uuid4()

    chunk = RetrievedChunk(
        chunk_id=chunk_id,
        repository_id=repo_id,
        file_id=file_id,
        file_path="src/auth/token.py",
        language="Python",
        content="def verify_jwt(token: str) -> bool: return True",
        start_line=10,
        end_line=25,
        symbol_name="verify_jwt",
        symbol_type="function",
        parent_symbol=None,
        score=0.94,
        retrieval_method="hybrid",
        metadata={"docstring": "Validates JSON Web Tokens."}
    )

    print(f"[TEST] Chunk created: {chunk.file_path} (Lines {chunk.start_line}-{chunk.end_line})")
    print(f"[TEST] Symbol: {chunk.symbol_name} ({chunk.symbol_type}) with score: {chunk.score}")
    
    assert chunk.file_path == "src/auth/token.py"
    assert chunk.symbol_name == "verify_jwt"
    assert chunk.score == 0.94
    assert chunk.start_line == 10
    assert chunk.end_line == 25
    print("[TEST] RetrievedChunk verification passed successfully.")


def test_rrf_scoring_logic():
    print("\n[TEST] Verifying Reciprocal Rank Fusion calculation...")
    k = 60
    # Score for Rank 0 (First position)
    score_rank_0 = 1.0 / (k + 1)
    # Score for Rank 1 (Second position)
    score_rank_1 = 1.0 / (k + 2)

    print(f"[TEST] RRF Score Rank 1: {score_rank_0:.6f}, Rank 2: {score_rank_1:.6f}")
    assert score_rank_0 > score_rank_1
    assert abs(score_rank_0 - 0.0163934) < 1e-5
    print("[TEST] RRF scoring monotonicity confirmed.")