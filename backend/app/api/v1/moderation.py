"""UGC Content Moderation API endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Literal, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.services.moderation import moderation_service

router = APIRouter(prefix="/moderation", tags=["moderation"])


class ModerateRequest(BaseModel):
    """Request body for content moderation check."""
    content: str = Field(..., min_length=1, max_length=10000, description="Content to moderate")
    content_type: Literal["post", "comment", "title", "bio"] = Field(
        default="post",
        description="Type of content being moderated"
    )


class ModerateResponse(BaseModel):
    """Response body for content moderation check."""
    status: Literal["pass", "review", "reject"] = Field(..., description="Moderation status")
    reason: Optional[str] = Field(None, description="Reason for rejection/flag")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    details: Optional[dict] = Field(None, description="Detailed moderation results")


@router.post("/check", response_model=ModerateResponse)
async def moderate_content(
    request: ModerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if user-generated content is safe for publication.
    
    Performs multi-layer moderation:
    1. Keyword filtering (fast, local)
    2. External content safety API (optional, more accurate)
    
    Returns:
    - status: "pass" (safe), "review" (needs manual review), "reject" (blocked)
    - reason: Explanation if not passed
    - confidence: AI confidence score (0.0-1.0)
    - details: Full moderation breakdown
    """
    try:
        # Call the moderation service (adapt parameter names)
        result = await moderation_service.moderate(
            text=request.content,
            user_id=str(current_user.id),
            context=request.content_type,
        )
        
        # Map internal result to API response
        if result.blocked:
            status = "reject"
            reason = ", ".join(result.reasons) if result.reasons else "Content blocked"
        elif not result.safe:
            status = "review"
            reason = ", ".join(result.reasons) if result.reasons else "Needs manual review"
        else:
            status = "pass"
            reason = None
        
        # Calculate confidence from available data
        if result.safety_result:
            confidence = result.safety_result.highest_confidence
        elif result.keyword_result:
            # Keyword filter: 1.0 if blocked, 0.0 if passed
            confidence = 1.0 if result.blocked else 0.9
        else:
            confidence = 1.0
        
        # Build details object
        details = {
            "keyword_checks": {
                "blocked": result.keyword_result.blocked if result.keyword_result else False,
                "matches": result.keyword_result.matches if result.keyword_result else [],
                "severity": result.keyword_result.highest_severity if result.keyword_result else 0,
            },
        }
        
        if result.safety_result:
            details["safety_checks"] = {
                "flagged_categories": [cat.value for cat in result.safety_result.flagged_categories],
                "overall_score": result.safety_result.highest_confidence,
            }
        
        return ModerateResponse(
            status=status,
            reason=reason,
            confidence=confidence,
            details=details,
        )
        
    except Exception as e:
        # Log error but don't expose internal details
        import logging
        logging.getLogger(__name__).error(f"Moderation error: {e}")
        raise AppException(ErrorCode.MODERATION_SERVICE_ERROR, 500, "Moderation service error")


@router.get("/health")
async def moderation_health():
    """Check if moderation service is operational."""
    return {
        "status": "ok",
        "service": "moderation",
        "version": "1.0.0",
    }
