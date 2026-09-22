"""CORS, rate limiting, and logging middleware."""

import logging
import time
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.redis import get_redis

logger = logging.getLogger(__name__)


def setup_cors(app):
    """Configure CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting using Redis sliding window."""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path.endswith("/health"):
            return await call_next(request)

        redis = await get_redis()
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}:{request.url.path}"

        # Determine rate limit
        # Only actual LLM generation endpoints (stream, free-chat, custom-input, onboarding) get the strict limit.
        # Reading dialogue state (/dialogue GET) is a DB read, not an LLM call — use normal limit.
        is_llm_write = (
            "/llm/" in request.url.path
            or "/dialogue/stream" in request.url.path
            or "/free-chat" in request.url.path
            or "/custom-input" in request.url.path
            or "/onboarding" in request.url.path
        )
        limit = settings.llm_rate_limit if is_llm_write else settings.api_rate_limit
        window = 60  # 1 minute

        # Check rate limit
        try:
            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, window)
            elif current > limit:
                return Response(
                    content='{"error_code": "RATE_LIMITED", "message": "Too many requests"}',
                    status_code=429,
                    media_type="application/json",
                )
        except Exception:
            # If Redis is down, allow request
            pass

        response = await call_next(request)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        # Log request (in production, use proper logging)
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        return response
