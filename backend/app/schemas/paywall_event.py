"""Paywall event Pydantic schemas (CR-016)."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class PaywallTriggerResponse(BaseModel):
    """Response schema for paywall trigger check."""
    should_show: bool
    display_type: Optional[str] = Field(description="modal/banner/toast")
    payload: Optional[Dict[str, Any]] = Field(description="Additional payload for UI")
    scene: str
    user_id: str


class RecordModalShownRequest(BaseModel):
    """Request schema for recording modal shown."""
    scene: str


class DailyModalCountResponse(BaseModel):
    """Response schema for daily modal count."""
    user_id: str
    date: str
    modal_count: int
    max_allowed: int


class DowngradeCheckResponse(BaseModel):
    """Response schema for downgrade check."""
    should_downgrade: bool
    reason: Optional[str] = None


class PaywallEventResponse(BaseModel):
    """Response schema for paywall event record."""
    id: str
    user_id: str
    scene: str
    display_type: str
    triggered_at: datetime

    model_config = {"from_attributes": True}
