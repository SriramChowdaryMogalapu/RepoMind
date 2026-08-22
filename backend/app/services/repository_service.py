# backend/app/services/repository_service.py
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.repository import Repository, RepositoryStatus
from app.models.file import File
from app.models.chunk import CodeChunk
from app.core.security import validate_and_parse_github_url
from app.core.errors import AppException
from fastapi import status


class RepositoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, repo_id: UUID) -> Repository:
        stmt = select(Repository).where(Repository.id == repo_id)
        result = await self.db.execute(stmt)
        repo = result.scalars().first()
        if not repo:
            raise AppException(
                code="REPOSITORY_NOT_FOUND",
                message="The requested repository does not exist.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        return repo

    async def get_by_full_name(self, full_name: str) -> Optional[Repository]:
        stmt = select(Repository).where(Repository.full_name == full_name.lower())
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def register_repository(self, url: str) -> Repository:
        parsed = validate_and_parse_github_url(url)

        existing_repo = await self.get_by_full_name(parsed.full_name)
        if existing_repo:
            return existing_repo

        new_repo = Repository(
            owner=parsed.owner,
            name=parsed.repo,
            full_name=parsed.full_name,
            url=parsed.normalized_url,
            status=RepositoryStatus.PENDING
        )
        self.db.add(new_repo)
        await self.db.flush()
        await self.db.refresh(new_repo)
        return new_repo

    async def list_repositories(self, limit: int = 50, offset: int = 0) -> List[Repository]:
        stmt = select(Repository).order_by(Repository.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_repository(self, repo_id: UUID) -> bool:
        repo = await self.get_by_id(repo_id)
        await self.db.delete(repo)
        await self.db.commit()
        return True

    async def get_repository_files(self, repo_id: UUID) -> List[File]:
        stmt = select(File).where(File.repository_id == repo_id).order_by(File.path.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_file_by_path(self, repo_id: UUID, path: str) -> Optional[File]:
        stmt = select(File).where(File.repository_id == repo_id, File.path == path)
        result = await self.db.execute(stmt)
        return result.scalars().first()