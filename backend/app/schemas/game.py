"""Game schemas for CR-038 Corvus frontend entry."""

from typing import Optional
from pydantic import BaseModel, Field


class PlayerCandidateCreate(BaseModel):
    """Request body for POST /api/v1/game/player/candidates.

    CR-038 AC-038-003~006: Create a player character candidate.
    - name: required, ≤100 chars
    - personality: optional
    - backstory: optional
    - appearance: optional
    - initial_inventory: NOT accepted from user (managed by backend)
    """

    name: str = Field(..., max_length=100, description="角色名字（必填，≤100字符）")
    personality: Optional[str] = Field(None, description="角色性格描述（可选）")
    backstory: Optional[str] = Field(None, description="角色背景故事（可选）")
    appearance: Optional[str] = Field(None, description="角色外貌描述（可选）")


class CharacterResponse(BaseModel):
    """Response schema for a single playable character.

    CR-038 AC-038-026: GET /api/v1/game/scripts/{script_id}/characters returns
    a list of playable characters with these fields.
    """

    id: str = Field(..., description="角色 ID (UUID v4)")
    name: str = Field(..., description="角色名字")
    description: Optional[str] = Field(None, description="角色描述")
    avatar_url: Optional[str] = Field(None, description="角色头像 URL")
    play_description: Optional[str] = Field(None, description="角色游玩描述")
