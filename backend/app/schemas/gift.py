"""Gift Pydantic schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GiftRequest(BaseModel):
    """Request schema for sending a gift."""
    character_id: str
    gift_id: str
    quantity: int = 1


class GiftResponse(BaseModel):
    """Response schema after sending a gift."""
    status: str
    message: str
    affection_delta: int
    new_affection: int
    fragments_spent: int
    remaining_fragments: int


class GiftRecordResponse(BaseModel):
    """Response schema for gift history record."""
    id: str
    character_id: str
    character_name: str
    gift_id: str
    gift_name: str
    quantity: int
    affection_delta: int
    created_at: str
