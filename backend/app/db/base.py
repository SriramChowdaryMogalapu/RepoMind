# backend/app/db/base.py
# Import all SQLAlchemy models here so Alembic and Base have full visibility
from app.db.session import Base
from app.models.repository import Repository, RepositoryStatus
from app.models.file import File
from app.models.chunk import CodeChunk

__all__ = ["Base", "Repository", "RepositoryStatus", "File", "CodeChunk"]