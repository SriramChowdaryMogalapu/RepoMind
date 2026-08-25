# backend/app/ingestion/orchestrator.py
import hashlib
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.errors import AppException
from app.embeddings.factory import get_embedding_provider
from app.ingestion.filter import detect_language, is_file_supported
from app.models.chunk import CodeChunk
from app.models.file import File
from app.models.repository import Repository, RepositoryStatus
from app.parsing.dispatcher import parse_file_to_chunks
from app.services.github import GitHubClient


class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.github = GitHubClient()
        self.embedding_provider = get_embedding_provider()

    async def start_ingestion(self, repository_id: UUID) -> Repository:
        stmt = (
            select(Repository)
            .where(Repository.id == repository_id)
            .options(selectinload(Repository.files))
        )
        res = await self.db.execute(stmt)
        repo = res.scalars().first()

        if not repo:
            raise AppException(code="REPOSITORY_NOT_FOUND", message="Repository not found.")

        try:
            # Stage 1: CLONING / METADATA FETCH
            repo.status = RepositoryStatus.CLONING
            await self.db.commit()

            meta = await self.github.get_repository_metadata(repo.owner, repo.name)
            repo.default_branch = meta.get("default_branch", "main")
            repo.description = meta.get("description")
            repo.language = meta.get("language")
            repo.stars = meta.get("stargazers_count", 0)
            repo.forks = meta.get("forks_count", 0)

            tree_items = await self.github.get_file_tree(repo.owner, repo.name, repo.default_branch)

            valid_files = []
            for item in tree_items:
                if item.get("type") == "blob":
                    path = item.get("path", "")
                    size = item.get("size", 0)
                    if is_file_supported(path, size, max_file_size_kb=settings.MAX_FILE_SIZE_KB):
                        valid_files.append(item)

            if len(valid_files) > settings.MAX_FILES:
                repo.status = RepositoryStatus.FAILED
                repo.error_message = (
                    f"Repository exceeds maximum file count limit of {settings.MAX_FILES}."
                )
                await self.db.commit()
                return repo

            # Clean previous files if re-indexing
            for f in repo.files:
                await self.db.delete(f)

            file_entities = []
            for f_item in valid_files:
                path = f_item.get("path")
                size = f_item.get("size", 0)
                file_hash = f_item.get("sha") or hashlib.sha256(path.encode()).hexdigest()
                lang = detect_language(path)

                new_file = File(
                    repository_id=repo.id,
                    path=path,
                    language=lang,
                    size_bytes=size,
                    file_hash=file_hash,
                )
                file_entities.append(new_file)
                self.db.add(new_file)

            repo.file_count = len(file_entities)

            # Stage 2: PARSING & CHUNKING
            repo.status = RepositoryStatus.PARSING
            await self.db.commit()
            await self.db.refresh(repo)

            all_chunks: list[CodeChunk] = []
            for file_obj in file_entities:
                content = await self.github.fetch_file_content(
                    owner=repo.owner,
                    repo=repo.name,
                    path=file_obj.path,
                    default_branch=repo.default_branch,
                )
                if not content:
                    continue

                raw_chunks = parse_file_to_chunks(content, file_obj.language or "Unknown")
                for r_chunk in raw_chunks:
                    chunk = CodeChunk(
                        repository_id=repo.id,
                        file_id=file_obj.id,
                        content=r_chunk.content,
                        start_line=r_chunk.start_line,
                        end_line=r_chunk.end_line,
                        symbol_name=r_chunk.symbol_name,
                        symbol_type=r_chunk.symbol_type,
                        parent_symbol=r_chunk.parent_symbol,
                        chunk_metadata=r_chunk.metadata,
                    )
                    self.db.add(chunk)
                    all_chunks.append(chunk)

            repo.chunk_count = len(all_chunks)

            # Stage 3: EMBEDDING
            repo.status = RepositoryStatus.EMBEDDING
            await self.db.commit()

            if all_chunks:
                batch_size = settings.EMBEDDING_BATCH_SIZE
                for i in range(0, len(all_chunks), batch_size):
                    batch = all_chunks[i : i + batch_size]
                    batch_texts = [c.content for c in batch]
                    embeddings = await self.embedding_provider.embed_batch(batch_texts)
                    for chunk, emb in zip(batch, embeddings, strict=False):
                        chunk.embedding = emb

            # Stage 4: READY
            repo.status = RepositoryStatus.READY
            repo.indexed_at = datetime.utcnow()
            repo.error_message = None
            await self.db.commit()
            await self.db.refresh(repo)
            return repo

        except Exception as e:
            repo.status = RepositoryStatus.FAILED
            repo.error_message = str(e)
            await self.db.commit()
            raise
