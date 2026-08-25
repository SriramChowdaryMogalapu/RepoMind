# backend/app/schemas/repository.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.repository import RepositoryStatus


class RepositoryCreateRequest(BaseModel):
    url: str = Field(..., example="https://github.com/fastapi/fastapi")


class RepositoryResponse(BaseModel):
    id: UUID
    owner: str
    name: str
    full_name: str
    url: str
    default_branch: str
    description: str | None = None
    language: str | None = None
    stars: int = 0
    forks: int = 0
    status: RepositoryStatus
    error_message: str | None = None
    file_count: int = 0
    chunk_count: int = 0
    indexed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RepositoryStatusResponse(BaseModel):
    id: UUID
    status: RepositoryStatus
    file_count: int
    chunk_count: int
    error_message: str | None = None
