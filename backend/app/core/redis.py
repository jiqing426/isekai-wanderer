"""Redis client and session management utilities."""

import json
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as aioredis
from app.core.config import settings

# Global Redis client
redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get Redis client instance (singleton)."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


# ============ Session Management ============

SESSION_PREFIX = "session:"
SESSION_TTL = timedelta(minutes=settings.jwt_access_token_expire_minutes)


async def create_session(user_id: str, session_data: dict) -> str:
    """Create a new session in Redis."""
    redis = await get_redis()
    import uuid
    session_id = str(uuid.uuid4())
    key = f"{SESSION_PREFIX}{session_id}"
    await redis.setex(key, int(SESSION_TTL.total_seconds()), json.dumps(session_data))
    return session_id


async def get_session(session_id: str) -> Optional[dict]:
    """Get session data from Redis."""
    redis = await get_redis()
    key = f"{SESSION_PREFIX}{session_id}"
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None


async def update_session(session_id: str, session_data: dict, extend_ttl: bool = True):
    """Update session data in Redis."""
    redis = await get_redis()
    key = f"{SESSION_PREFIX}{session_id}"
    await redis.setex(key, int(SESSION_TTL.total_seconds()), json.dumps(session_data))


async def delete_session(session_id: str):
    """Delete session from Redis."""
    redis = await get_redis()
    key = f"{SESSION_PREFIX}{session_id}"
    await redis.delete(key)


async def extend_session(session_id: str):
    """Extend session TTL."""
    redis = await get_redis()
    key = f"{SESSION_PREFIX}{session_id}"
    await redis.expire(key, int(SESSION_TTL.total_seconds()))


# ============ Rate Limiting ============

RATE_LIMIT_PREFIX = "ratelimit:"


async def check_rate_limit(key: str, limit: int, window_seconds: int = 60) -> tuple[bool, int]:
    """
    Check if rate limit is exceeded.
    Returns: (allowed: bool, remaining: int)
    """
    redis = await get_redis()
    full_key = f"{RATE_LIMIT_PREFIX}{key}"
    
    # Increment counter
    current = await redis.incr(full_key)
    
    # Set expiry on first request
    if current == 1:
        await redis.expire(full_key, window_seconds)
    
    remaining = max(0, limit - current)
    allowed = current <= limit
    
    return allowed, remaining


async def get_rate_limit_info(key: str) -> tuple[int, int]:
    """Get current rate limit count and TTL."""
    redis = await get_redis()
    full_key = f"{RATE_LIMIT_PREFIX}{key}"
    
    current = await redis.get(full_key)
    ttl = await redis.ttl(full_key)
    
    count = int(current) if current else 0
    remaining_ttl = ttl if ttl > 0 else 0
    
    return count, remaining_ttl


# ============ Generic Cache ============

CACHE_PREFIX = "cache:"


async def cache_get(key: str) -> Optional[Any]:
    """Get cached value."""
    redis = await get_redis()
    full_key = f"{CACHE_PREFIX}{key}"
    data = await redis.get(full_key)
    if data:
        return json.loads(data)
    return None


async def cache_set(key: str, value: Any, ttl: int = 300):
    """Set cached value with TTL (default 5 minutes)."""
    redis = await get_redis()
    full_key = f"{CACHE_PREFIX}{key}"
    await redis.setex(full_key, ttl, json.dumps(value, default=str))


async def cache_delete(key: str):
    """Delete cached value."""
    redis = await get_redis()
    full_key = f"{CACHE_PREFIX}{key}"
    await redis.delete(full_key)


async def cache_delete_pattern(pattern: str):
    """Delete all keys matching pattern."""
    redis = await get_redis()
    full_pattern = f"{CACHE_PREFIX}{pattern}"
    async for key in redis.scan_iter(match=full_pattern):
        await redis.delete(key)
