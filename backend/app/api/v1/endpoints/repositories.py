# backend/app/api/v1/endpoints/repositories.py
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.errors import AppException, NotFoundException
from app.core.security import validate_and_parse_github_url
from app.db.session import AsyncSessionLocal, get_db
from app.ingestion.orchestrator import IngestionService
from app.llm.context_builder import build_documentation_messages
from app.llm.factory import get_llm_provider
from app.models.chunk import CodeChunk
from app.models.file import File
from app.models.repository import Repository, RepositoryStatus
from app.retrieval.base import RetrievedChunk
from app.retrieval.hybrid_retriever import HybridRetriever
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.file import FileItemResponse, FileListResponse
from app.schemas.repository import (
    RepositoryCreateRequest,
    RepositoryResponse,
    RepositoryStatusResponse,
)
from app.schemas.retrieval import (
    RetrievalQueryRequest,
    RetrievalResponse,
    RetrievedChunkResponse,
)
from app.services.chat_service import ChatService

router = APIRouter()


async def run_ingestion_task(repo_id: UUID, db_factory):
    async with db_factory() as session:
        service = IngestionService(session)
        await service.start_ingestion(repo_id)


@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def register_repository(payload: RepositoryCreateRequest, db: AsyncSession = Depends(get_db)):
    try:
        parsed = validate_and_parse_github_url(payload.url)
    except ValueError as e:
        raise AppException(
            code="INVALID_URL", message=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        ) from e

    stmt = select(Repository).where(Repository.full_name == parsed.full_name)
    result = await db.execute(stmt)
    existing_repo = result.scalars().first()

    if existing_repo:
        return existing_repo

    new_repo = Repository(
        owner=parsed.owner,
        name=parsed.repo,
        full_name=parsed.full_name,
        url=parsed.normalized_url,
        status=RepositoryStatus.PENDING,
    )
    db.add(new_repo)
    await db.flush()
    await db.refresh(new_repo)
    return new_repo


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(repo_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Repository).where(Repository.id == repo_id)
    result = await db.execute(stmt)
    repo = result.scalars().first()
    if not repo:
        raise AppException(
            code="REPOSITORY_NOT_FOUND",
            message="Repository was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return repo


@router.get("/{repo_id}/status", response_model=RepositoryStatusResponse)
async def get_repository_status(repo_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Repository).where(Repository.id == repo_id)
    result = await db.execute(stmt)
    repo = result.scalars().first()
    if not repo:
        raise AppException(
            code="REPOSITORY_NOT_FOUND",
            message="Repository was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return RepositoryStatusResponse(
        id=repo.id,
        status=repo.status,
        file_count=repo.file_count,
        chunk_count=repo.chunk_count,
        error_message=repo.error_message,
    )


@router.post("/{repo_id}/index", response_model=RepositoryStatusResponse)
async def trigger_indexing(
    repo_id: UUID, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)
):
    stmt = select(Repository).where(Repository.id == repo_id)
    result = await db.execute(stmt)
    repo = result.scalars().first()

    if not repo:
        raise AppException(code="NOT_FOUND", message="Repository not found.", status_code=404)

    background_tasks.add_task(run_ingestion_task, repo.id, AsyncSessionLocal)

    repo.status = RepositoryStatus.CLONING
    await db.commit()

    return RepositoryStatusResponse(
        id=repo.id,
        status=repo.status,
        file_count=repo.file_count,
        chunk_count=repo.chunk_count,
        error_message=None,
    )


@router.get("/{repo_id}/files", response_model=FileListResponse)
async def get_repository_files(repo_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(File).where(File.repository_id == repo_id)
    result = await db.execute(stmt)
    files = result.scalars().all()
    return FileListResponse(
        repository_id=repo_id,
        total=len(files),
        files=[
            FileItemResponse(id=f.id, path=f.path, language=f.language, size_bytes=f.size_bytes)
            for f in files
        ],
    )


@router.post("/{repo_id}/retrieve", response_model=RetrievalResponse)
async def retrieve_code_chunks(
    repo_id: UUID, payload: RetrievalQueryRequest, db: AsyncSession = Depends(get_db)
):
    stmt = select(Repository).where(Repository.id == repo_id)
    result = await db.execute(stmt)
    repo = result.scalars().first()
    if not repo:
        raise AppException(
            code="REPOSITORY_NOT_FOUND", message="Repository not found.", status_code=404
        )

    retriever = HybridRetriever(db)
    chunks = await retriever.retrieve(
        repository_id=repo_id,
        query=payload.query,
        top_k=payload.top_k,
        path_filter=payload.path_filter,
    )

    return RetrievalResponse(
        repository_id=repo_id,
        query=payload.query,
        total_candidates=len(chunks),
        results=[
            RetrievedChunkResponse(
                chunk_id=c.chunk_id,
                file_path=c.file_path,
                language=c.language,
                content=c.content,
                start_line=c.start_line,
                end_line=c.end_line,
                symbol_name=c.symbol_name,
                symbol_type=c.symbol_type,
                parent_symbol=c.parent_symbol,
                score=c.score,
                retrieval_method=c.retrieval_method,
                metadata=c.metadata,
            )
            for c in chunks
        ],
    )


@router.get("/{repository_id}/files/content")
async def get_file_content(
    repository_id: UUID,
    path: str = Query(..., description="Relative file path"),
    db: AsyncSession = Depends(get_db),
):
    # 1. Fetch the file metadata record
    stmt = select(File).where(
        File.repository_id == repository_id, File.path == path.strip().lstrip("/")
    )
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()

    if not file_record:
        raise NotFoundException(message=f"File '{path}' not found in repository.")

    # 2. Fetch all code chunks for this file ordered by start_line
    chunk_stmt = (
        select(CodeChunk)
        .where(CodeChunk.file_id == file_record.id)
        .order_by(CodeChunk.start_line.asc())
    )
    chunk_result = await db.execute(chunk_stmt)
    chunks = chunk_result.scalars().all()

    if not chunks:
        file_content = "// No code chunks available for this file."
    else:
        # Deduplicate and join chunks in sequential order
        content_blocks = []
        for c in chunks:
            if c.content and (not content_blocks or content_blocks[-1] != c.content):
                content_blocks.append(c.content)
        file_content = "\n\n".join(content_blocks)

    return {
        "path": file_record.path,
        "language": getattr(file_record, "language", "text") or "text",
        "content": file_content,
    }


@router.get("/{repository_id}/documentation", response_class=PlainTextResponse)
async def get_repository_documentation(
    repository_id: UUID,
    path: str | None = Query(default=None, description="Optional relative file path"),
    db: AsyncSession = Depends(get_db),
):
    repo_result = await db.execute(select(Repository).where(Repository.id == repository_id))
    repo = repo_result.scalar_one_or_none()
    if not repo:
        raise NotFoundException(message="Repository not found.")

    file_query = select(File).where(File.repository_id == repository_id)
    if path:
        file_query = file_query.where(File.path == path.strip().lstrip("/"))
    file_result = await db.execute(file_query.order_by(File.path.asc()))
    files = file_result.scalars().all()
    if path and not files:
        raise NotFoundException(message=f"File '{path}' not found in repository.")

    documentation_chunks: list[RetrievedChunk] = []
    for file_record in files:
        chunk_result = await db.execute(
            select(CodeChunk)
            .where(CodeChunk.file_id == file_record.id)
            .order_by(CodeChunk.start_line.asc())
        )
        chunks = chunk_result.scalars().all()
        documentation_chunks.extend(
            RetrievedChunk(
                chunk_id=chunk.id,
                repository_id=repository_id,
                file_id=file_record.id,
                file_path=file_record.path,
                language=file_record.language,
                content=chunk.content,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                symbol_name=chunk.symbol_name,
                symbol_type=chunk.symbol_type,
                parent_symbol=chunk.parent_symbol,
                score=1.0,
                retrieval_method="documentation",
            )
            for chunk in chunks
        )

    messages, _ = build_documentation_messages(documentation_chunks)
    llm_response = await get_llm_provider().generate_response(messages, max_tokens=5000)
    filename = f"{files[0].path.split('/')[-1]}.md" if path else "repomind-documentation.md"

    return PlainTextResponse(
        content=llm_response.content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{repo_id}/chat", response_model=ChatResponse)
async def chat_with_repository(
    repo_id: UUID, payload: ChatRequest, db: AsyncSession = Depends(get_db)
):
    service = ChatService(db)
    return await service.answer_question(repository_id=repo_id, request=payload)
