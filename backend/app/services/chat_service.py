# backend/app/services/chat_service.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.repository import Repository
from app.retrieval.hybrid_retriever import HybridRetriever
from app.llm.factory import get_llm_provider
from app.llm.context_builder import build_rag_messages
from app.schemas.chat import ChatRequest, ChatResponse, SourceCitation
from app.core.errors import AppException
import logging
import time
from app.core.logging import setup_logging
from app.services.repository_service import RepositoryService

try:
    setup_logging()
    logger = logging.getLogger("repomind.api")
except e as Exception:
    print(f"Logger Setup Failed: {e}")


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.retriever = HybridRetriever(db)
        self.llm = get_llm_provider()
        self.repo_service = RepositoryService(db)

    def _build_github_url(self, repo: Repository, file_path: str, start_line: int, end_line: int) -> str:
        branch = repo.default_branch or "main"
        clean_path = file_path.lstrip("/")
        if start_line == end_line:
            line_fragment = f"#L{start_line}"
        else:
            line_fragment = f"#L{start_line}-L{end_line}"
        return f"https://github.com/{repo.owner}/{repo.name}/blob/{branch}/{clean_path}{line_fragment}"

    async def answer_question(self, repository_id: UUID, request: ChatRequest) -> ChatResponse:
        logger.info(f"Processing question for repo={repository_id}: '{request.question[:60]}...'")

        # 1. Fetch explicitly tagged files (if any)
        tagged_chunks = []
        if request.tagged_files:
            logger.info(f"Injecting {len(request.tagged_files)} tagged files: {request.tagged_files}")
            tagged_chunks = await self.retriever.get_tagged_file_chunks(
                repository_id=repository_id,
                file_paths=request.tagged_files
            )

        # 2. Perform hybrid retrieval for related context
        retrieved_candidates = await self.retriever.retrieve(
            repository_id=repository_id,
            query=request.question,
            top_k=request.top_k
        )

        # 3. Deduplicate (Tagged chunks take precedence)
        seen_chunk_ids = set()
        final_candidates = []

        for chunk in tagged_chunks + retrieved_candidates:
            if chunk.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk.chunk_id)
                final_candidates.append(chunk)

        logger.info(f"Constructing prompt with {len(final_candidates)} candidate chunks.")

        # 4. Assemble Grounded Messages & Query LLM
        messages, used_chunks = build_rag_messages(request.question, final_candidates)
        llm_response = await self.llm.generate_response(messages)

        logger.info(f"LLM generation complete via model={llm_response.model_name}")

        # 5. Build verified source links
        repo = await self.repo_service.get_by_id(repository_id)
        sources = [
            {
                "file_path": c.file_path,
                "start_line": c.start_line,
                "end_line": c.end_line,
                "symbol_name": c.symbol_name,
                "language": c.language,
                "github_url": f"{repo.url}/blob/{repo.default_branch}/{c.file_path}#L{c.start_line}-L{c.end_line}"
            }
            for c in used_chunks
        ]

        return ChatResponse(
            repository_id=repository_id,
            question=request.question,
            answer=llm_response.content,
            sources=sources,
            confidence="high" if len(used_chunks) > 0 else "low",
            model_name=llm_response.model_name
        )