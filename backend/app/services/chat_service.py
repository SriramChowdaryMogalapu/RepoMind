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


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.retriever = HybridRetriever(db)
        self.llm = get_llm_provider()

    def _build_github_url(self, repo: Repository, file_path: str, start_line: int, end_line: int) -> str:
        branch = repo.default_branch or "main"
        clean_path = file_path.lstrip("/")
        if start_line == end_line:
            line_fragment = f"#L{start_line}"
        else:
            line_fragment = f"#L{start_line}-L{end_line}"
        return f"https://github.com/{repo.owner}/{repo.name}/blob/{branch}/{clean_path}{line_fragment}"

    async def answer_question(self, repository_id: UUID, request: ChatRequest) -> ChatResponse:
        stmt = select(Repository).where(Repository.id == repository_id)
        result = await self.db.execute(stmt)
        repo = result.scalars().first()

        if not repo:
            raise AppException(code="REPOSITORY_NOT_FOUND", message="Repository not found.", status_code=404)

        # 1. Retrieve hybrid candidates
        candidates = await self.retriever.retrieve(
            repository_id=repository_id,
            query=request.question,
            top_k=request.top_k,
            path_filter=request.path_filter
        )

        # 2. Build context and enforce limits
        messages, used_chunks = build_rag_messages(
            query=request.question,
            retrieved_chunks=candidates
        )

        # 3. Generate grounded LLM response
        llm_resp = await self.llm.generate_response(messages)

        # 4. Construct validated source citations
        sources: List[SourceCitation] = []
        for chunk in used_chunks:
            github_url = self._build_github_url(
                repo=repo,
                file_path=chunk.file_path,
                start_line=chunk.start_line,
                end_line=chunk.end_line
            )
            sources.append(
                SourceCitation(
                    file_path=chunk.file_path,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    symbol_name=chunk.symbol_name,
                    language=chunk.language,
                    github_url=github_url
                )
            )

        # Evaluate confidence
        if not used_chunks or "not find enough evidence" in llm_resp.content.lower():
            confidence = "insufficient_evidence"
        elif len(used_chunks) >= 3:
            confidence = "high"
        else:
            confidence = "medium"

        return ChatResponse(
            repository_id=repository_id,
            question=request.question,
            answer=llm_resp.content,
            sources=sources,
            confidence=confidence,
            model_name=llm_resp.model_name
        )