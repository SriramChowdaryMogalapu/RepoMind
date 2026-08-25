# backend/app/api/v1/api.py
from fastapi import APIRouter

from app.api.v1.endpoints import repositories

api_router = APIRouter()

api_router.include_router(repositories.router, prefix="/repositories", tags=["Repositories"])
