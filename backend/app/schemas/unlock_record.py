"""Unlock record Pydantic schemas (CR-017)."""

from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class UnlockRecordCreate(BaseModel):
    """Schema for creating an unlock record."""
    unlock_type: str = Field(..., description="Type of unlock: cg/achievement/hidden_story/voice/exclusive_script/reward_float/multi_reward")
    content_id: str = Field(..., description="ID of the unlocked content")
    title: str = Field(..., description="Title of the unlock")
    description: Optional[str] = Field(None, description="Description of the unlock")
    image_url: Optional[str] = Field(None, description="Thumbnail image URL")
    rarity: Optional[str] = Field(None, description="Rarity level: R/SR/SSR")
    reward_data: Optional[Dict[str, Any]] = Field(None, description="Additional reward data")


class UnlockRecordResponse(BaseModel):
    """Schema for unlock record response."""
    id: UUID
    user_id: UUID
    unlock_type: str
    content_id: str
    title: str
    description: Optional[str]
    image_url: Optional[str]
    rarity: Optional[str]
    reward_data: Optional[Dict[str, Any]]
    unlocked_at: datetime
    viewed: bool
    created_at: datetime

    class Config:
        from_attributes = True

    @field_serializer('id', 'user_id')
    def serialize_uuid_fields(self, v):
        return str(v)


class UnlockBatchItem(BaseModel):
    """Schema for batch unlock item."""
    unlock_type: str
    content_id: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    rarity: Optional[str] = None
    reward_data: Optional[Dict[str, Any]] = None


class UnlockBatchRequest(BaseModel):
    """Schema for batch unlock request."""
    unlocks: List[UnlockBatchItem] = Field(..., description="List of unlocks to record")


class UnlockBatchResponse(BaseModel):
    """Schema for batch unlock response."""
    success: bool
    recorded_count: int
    records: List[UnlockRecordResponse]


class MarkViewedRequest(BaseModel):
    """Schema for marking unlock as viewed."""
    record_id: str = Field(..., description="ID of the unlock record to mark as viewed")


class MarkViewedResponse(BaseModel):
    """Schema for mark viewed response."""
    success: bool
    record_id: str
    viewed: bool


class UnlockListResponse(BaseModel):
    """Schema for unlock list response."""
    records: List[UnlockRecordResponse]
    total: int
