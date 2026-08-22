# backend/app/schemas/file.py
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class FileItemResponse(BaseModel):
    id: UUID
    path: str
    language: Optional[str]
    size_bytes: int

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    repository_id: UUID
    total: int
    files: List[FileItemResponse]