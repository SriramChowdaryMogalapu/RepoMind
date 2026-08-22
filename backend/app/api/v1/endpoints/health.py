# backend/app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db
from app.core.config import settings

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    """Liveness probe."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness probe checking database and vector extension."""
    db_status = "connected"
    vector_status = "available"

    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    try:
        result = await db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
        row = result.scalar_one_or_none()
        if not row:
            vector_status = "extension_missing"
    except Exception as e:
        vector_status = f"unhealthy: {str(e)}"

    is_ready = db_status == "connected" and vector_status == "available"

    return {
        "ready": is_ready,
        "database": db_status,
        "pgvector": vector_status
    }