"""Global exception handlers and error codes."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    """Base application exception."""

    def __init__(self, error_code: str, status_code: int, message: str):
        self.error_code = error_code
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)


# Error code constants
class ErrorCode:
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_EMAIL_NOT_VERIFIED = "AUTH_EMAIL_NOT_VERIFIED"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_FORBIDDEN = "AUTH_FORBIDDEN"
    SCRIPT_NOT_FOUND = "SCRIPT_NOT_FOUND"
    SCRIPT_LOCKED = "SCRIPT_LOCKED"
    GAME_SESSION_EXPIRED = "GAME_SESSION_EXPIRED"
    GAME_INVALID_CHOICE = "GAME_INVALID_CHOICE"
    LLM_GENERATION_FAILED = "LLM_GENERATION_FAILED"
    LLM_RATE_LIMITED = "LLM_RATE_LIMITED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    SUBSCRIPTION_ACTIVE = "SUBSCRIPTION_ACTIVE"
    DAILY_ALREADY_CHECKED_IN = "DAILY_ALREADY_CHECKED_IN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    # CR-003 Wave 4: API error format unification
    COLLECTION_NOT_FOUND = "COLLECTION_NOT_FOUND"
    OAUTH_UNSUPPORTED_PROVIDER = "OAUTH_UNSUPPORTED_PROVIDER"
    OAUTH_RATE_LIMITED = "OAUTH_RATE_LIMITED"
    OAUTH_REGISTRATION_LIMIT = "OAUTH_REGISTRATION_LIMIT"
    PAYMENT_UNKNOWN_PLAN = "PAYMENT_UNKNOWN_PLAN"
    INVALID_SCRIPT_ID = "INVALID_SCRIPT_ID"
    SHARE_NOT_FOUND = "SHARE_NOT_FOUND"
    UGC_FORBIDDEN_CONTENT = "UGC_FORBIDDEN_CONTENT"
    UGC_POST_NOT_FOUND = "UGC_POST_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    MODERATION_SERVICE_ERROR = "MODERATION_SERVICE_ERROR"
    AUTH_USER_NOT_FOUND = "AUTH_USER_NOT_FOUND"
    # CR-003 Wave 1a: discover + characters
    CHARACTER_NOT_FOUND = "CHARACTER_NOT_FOUND"
    GIFT_FAILED = "GIFT_FAILED"
    DISCOVER_ERROR = "DISCOVER_ERROR"
    INVALID_CHARACTER_ID = "INVALID_CHARACTER_ID"
    # CR-003 Wave 1b: saves + shards
    SAVE_NOT_FOUND = "SAVE_NOT_FOUND"
    SAVE_SESSION_NOT_FOUND = "SAVE_SESSION_NOT_FOUND"
    SAVE_FORK_FAILED = "SAVE_FORK_FAILED"
    ENDING_PROGRESS_ERROR = "ENDING_PROGRESS_ERROR"
    # CR-003 Wave 1c Part A: achievements + daily tasks + activity
    ACHIEVEMENT_NOT_FOUND = "ACHIEVEMENT_NOT_FOUND"
    ACHIEVEMENT_ALREADY_UNLOCKED = "ACHIEVEMENT_ALREADY_UNLOCKED"
    ACHIEVEMENT_NOT_UNLOCKED = "ACHIEVEMENT_NOT_UNLOCKED"
    ACHIEVEMENT_ALREADY_CLAIMED = "ACHIEVEMENT_ALREADY_CLAIMED"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_NOT_COMPLETED = "TASK_NOT_COMPLETED"
    TASK_ALREADY_CLAIMED = "TASK_ALREADY_CLAIMED"
    ACTIVITY_CHEST_NOT_ELIGIBLE = "ACTIVITY_CHEST_NOT_ELIGIBLE"
    ACTIVITY_CHEST_ALREADY_CLAIMED = "ACTIVITY_CHEST_ALREADY_CLAIMED"
    # CR-003 Wave 1c Part C: recap + memory visibility
    INVALID_REQUEST = "INVALID_REQUEST"
    ACCESS_DENIED = "ACCESS_DENIED"
    NOT_FOUND = "NOT_FOUND"
    RECAP_GENERATION_FAILED = "RECAP_GENERATION_FAILED"
    MEMORY_NOT_FOUND = "MEMORY_NOT_FOUND"
    # CR-008 Fragment mall
    GOODS_NOT_FOUND = "GOODS_NOT_FOUND"
    GOODS_OUT_OF_STOCK = "GOODS_OUT_OF_STOCK"
    GOODS_LIMIT_REACHED = "GOODS_LIMIT_REACHED"
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"


async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error_code": ErrorCode.VALIDATION_ERROR, "message": str(exc.errors())},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error_code": ErrorCode.INTERNAL_ERROR, "message": "Internal server error"},
    )
