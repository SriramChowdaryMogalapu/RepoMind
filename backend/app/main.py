# backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.errors import AppException, app_exception_handler, generic_exception_handler
from app.core.rate_limiter import rate_limit_middleware
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    logger.info(f"--> {request.method} {request.url.path}")
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    status_code = response.status_code
    
    if status_code < 400:
        logger.info(f"<-- {request.method} {request.url.path} [{status_code}] ({duration_ms:.1f}ms)")
    else:
        logger.error(f"<-- {request.method} {request.url.path} [{status_code}] ({duration_ms:.1f}ms)")
    return response

# Custom Rate Limiter Middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)

# CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# API Routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}