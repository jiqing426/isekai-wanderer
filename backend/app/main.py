"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.exceptions import app_exception_handler, validation_exception_handler, generic_exception_handler, AppException
from app.middleware import setup_cors, RateLimitMiddleware, LoggingMiddleware
from app.api.v1 import api_router
from app.core.redis import close_redis
from fastapi.exceptions import RequestValidationError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    # HIGH-003: Warn if using weak JWT secret
    import sys
    if settings.jwt_secret == "change-me-local-only":
        print("\n" + "="*70, file=sys.stderr)
        print("⚠️  SECURITY WARNING: Using default JWT secret!", file=sys.stderr)
        print("   Set JWT_SECRET environment variable for production!", file=sys.stderr)
        print("="*70 + "\n", file=sys.stderr)
    
    # Start daily cron tasks
    import asyncio
    from app.core.database import async_session_factory
    from app.api.v1.subscription import run_subscription_expiry_check, run_monthly_fragment_grant
    
    async def daily_tasks():
        """Run daily subscription checks."""
        while True:
            await asyncio.sleep(86400)  # 24 hours
            try:
                async with async_session_factory() as session:
                    # Check expired subscriptions
                    downgraded = await run_subscription_expiry_check(session)
                    if downgraded:
                        print(f"[CRON] Downgraded {downgraded} expired subscriptions")
                    
                    # Grant monthly fragments
                    granted = await run_monthly_fragment_grant(session)
                    if granted:
                        print(f"[CRON] Granted monthly fragments to {granted} users")
            except Exception as e:
                print(f"[CRON] Error in daily tasks: {e}")
    
    task = asyncio.create_task(daily_tasks())
    
    yield
    
    # Shutdown
    task.cancel()
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Middleware
setup_cors(app)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Mock 数据中间件（优先于真实路由）
from app.mock_middleware import MockMiddleware
app.add_middleware(MockMiddleware)

# Routes
app.include_router(api_router)

# Static files for uploaded images
import os
static_dir = "/app/static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
async def health_check():
    """Root-level health check (no auth, no DB)."""
    return {"status": "ok"}
