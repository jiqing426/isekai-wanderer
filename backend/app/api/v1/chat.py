"""Free chat API — CR-007 Task 3 (v4.4 dual-agent architecture).

Provides:
- POST /chat/free — Free chat with character (companion agent)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.services.free_chat_service import free_chat_service
from app.api.v1.auth import get_current_user_id

router = APIRouter(prefix="/chat", tags=["chat"])


class FreeChatRequest(BaseModel):
    character_id: str
    message: str
    session_id: Optional[str] = None


class FreeChatResponse(BaseModel):
    reply: str
    affection_change: int = 0
    emotion: str = "neutral"
    character_id: str
    session_id: str


@router.post("/free", response_model=FreeChatResponse)
async def send_free_chat(
    request: FreeChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    CR-007 Task 3: Free chat with character (companion agent).
    
    This endpoint uses the companion agent which:
    - Does NOT advance the plot
    - Does NOT change affection (affection_change always 0)
    - Does NOT spoil unplayed content
    - Injects character persona
    - User-isolated conversations
    """
    result = await free_chat_service.send_message(
        db=db,
        user_id=user_id,
        character_id=request.character_id,
        message=request.message,
        session_id=request.session_id,
    )
    return FreeChatResponse(
        reply=result.get("reply", ""),
        affection_change=0,
        emotion=result.get("emotion", "neutral"),
        character_id=result.get("character_id", request.character_id),
        session_id=result.get("session_id", ""),
    )


@router.post("/demo", response_model=FreeChatResponse)
async def demo_chat(
    request: FreeChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Demo chat for onboarding (no authentication required).
    
    This endpoint provides a demo experience for new users
    without requiring authentication. Returns mock response.
    """
    # For demo purposes, return a simple mock response without database operations
    return FreeChatResponse(
        reply=f"你好！我是 {request.character_id}，很高兴见到你。这是一个演示对话。",
        affection_change=0,
        emotion="neutral",
        character_id=request.character_id,
        session_id="demo-session",
    )
