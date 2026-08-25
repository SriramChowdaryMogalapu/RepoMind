# backend/app/schemas/file.py
from uuid import UUID

from pydantic import BaseModel


class FileItemResponse(BaseModel):
    id: UUID
    path: str
    language: str | None
    size_bytes: int

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    repository_id: UUID
    total: int
    files: list[FileItemResponse]
