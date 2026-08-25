# backend/app/core/rate_limiter.py
import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

from app.core.config import settings


class InMemoryRateLimiter:
    """
    In-memory sliding window rate limiter per client IP.
    """

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60.0

        # Prune requests older than 1 minute
        self.requests[client_ip] = [ts for ts in self.requests[client_ip] if ts > window_start]

        if len(self.requests[client_ip]) >= self.rpm:
            return False

        self.requests[client_ip].append(now)
        return True


rate_limiter = InMemoryRateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)


async def rate_limit_middleware(request: Request, call_next):
    # Bypass health checks from rate limiting
    if request.url.path.endswith("/health") or request.method == "OPTIONS":
        return await call_next(request)

    client_ip = request.client.host if request.client else "127.0.0.1"
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before making more requests.",
        )

    return await call_next(request)
