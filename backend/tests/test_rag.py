# backend/tests/test_rag.py
import uuid

import pytest

from app.llm.context_builder import build_rag_messages
from app.llm.factory import get_llm_provider
from app.llm.mock_provider import MockLLMProvider
from app.retrieval.base import RetrievedChunk


@pytest.mark.asyncio
async def test_rag_context_building_and_mock_generation():
    print("\n[TEST] Testing RAG prompt assembly and ground-truth enforcement...")
    repo_id = uuid.uuid4()
    chunks = [
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            repository_id=repo_id,
            file_id=uuid.uuid4(),
            file_path="src/auth/jwt.py",
            language="Python",
            content="def decode_token(token: str): return {'user': 'admin'}",
            start_line=15,
            end_line=25,
            symbol_name="decode_token",
            symbol_type="function",
            score=0.92,
            retrieval_method="hybrid",
        )
    ]

    query = "How is JWT token decoding handled?"
    print(f"[TEST] Building context for query: '{query}' with {len(chunks)} chunks.")
    messages, used = build_rag_messages(query, chunks)

    assert len(messages) == 2
    assert messages[0].role == "system"
    assert "UNTRUSTED DATA" in messages[0].content
    assert "src/auth/jwt.py" in messages[1].content
    print("[TEST] Context assembled with system delimiters and file paths.")

    llm = MockLLMProvider()
    resp = await llm.generate_response(messages)
    print(f"[TEST] Mock LLM Response: {resp.content}")

    assert "src/auth/jwt.py" in resp.content
    assert "decode_token" in resp.content
    print("[TEST] Grounded answer generation verified.")


@pytest.mark.asyncio
async def test_insufficient_evidence_response():
    print("\n[TEST] Testing insufficient evidence behavior when no chunks retrieved...")
    query = "What is the secret deployment key?"
    messages, used = build_rag_messages(query, [])

    llm = MockLLMProvider()
    resp = await llm.generate_response(messages)
    print(f"[TEST] Empty context response: '{resp.content}'")

    assert "not find enough evidence" in resp.content.lower()
    print("[TEST] Correctly handled zero-evidence query without hallucinations.")


def test_llm_factory_resolution():
    print("\n[TEST] Testing get_llm_provider() factory resolution...")
    provider = get_llm_provider()
    assert isinstance(provider, MockLLMProvider)
    print(f"[TEST] Successfully resolved default LLM provider: {type(provider).__name__}")
