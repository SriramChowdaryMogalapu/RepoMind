# backend/tests/test_integration.py
import pytest
import uuid
from app.core.security import validate_and_parse_github_url
from app.parsing.dispatcher import parse_file_to_chunks
from app.embeddings.mock_provider import MockEmbeddingProvider
from app.retrieval.base import RetrievedChunk
from app.llm.context_builder import build_rag_messages
from app.llm.mock_provider import MockLLMProvider


@pytest.mark.asyncio
async def test_full_pipeline_flow():
    print("\n[INTEGRATION TEST] Starting complete repository indexing -> retrieval -> RAG generation flow...")
    
    # 1. URL Validation
    url = "https://github.com/fastapi/fastapi"
    parsed = validate_and_parse_github_url(url)
    print(f"[INTEGRATION TEST] Stage 1 - Validated: {parsed.full_name}")
    assert parsed.owner == "fastapi"

    # 2. Source Parsing & Structural AST Chunking
    sample_code = """
class FastAPIServer:
    def __init__(self, port: int = 8000):
        self.port = port

    def run_server(self):
        return f"Listening on {self.port}"
"""
    raw_chunks = parse_file_to_chunks(sample_code, "Python")
    print(f"[INTEGRATION TEST] Stage 2 - Extracted {len(raw_chunks)} structural chunks from source code.")
    assert len(raw_chunks) >= 2

    # 3. Embedding Generation
    embedding_provider = MockEmbeddingProvider(dimension=1536)
    chunk_texts = [c.content for c in raw_chunks]
    embeddings = await embedding_provider.embed_batch(chunk_texts)
    print(f"[INTEGRATION TEST] Stage 3 - Generated {len(embeddings)} batch embeddings (Dim: {len(embeddings[0])}).")
    assert len(embeddings) == len(raw_chunks)

    # 4. Context Assembly from Simulated Search
    repo_id = uuid.uuid4()
    retrieved = [
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            repository_id=repo_id,
            file_id=uuid.uuid4(),
            file_path="app/server.py",
            language="Python",
            content=raw_chunks[0].content,
            start_line=raw_chunks[0].start_line,
            end_line=raw_chunks[0].end_line,
            symbol_name=raw_chunks[0].symbol_name,
            symbol_type=raw_chunks[0].symbol_type,
            score=0.98,
            retrieval_method="hybrid"
        )
    ]

    messages, used = build_rag_messages("Where is the server configured?", retrieved)
    print(f"[INTEGRATION TEST] Stage 4 - Assembled prompt context ({len(used)} chunk included).")
    assert len(used) == 1

    # 5. Grounded LLM Response
    llm = MockLLMProvider()
    response = await llm.generate_response(messages)
    print(f"[INTEGRATION TEST] Stage 5 - Grounded LLM Response received:\n'{response.content}'")
    
    assert "app/server.py" in response.content
    assert len(response.content) > 20
    print("[INTEGRATION TEST] End-to-end pipeline verified successfully.")