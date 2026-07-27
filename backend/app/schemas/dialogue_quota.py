"""Dialogue quota Pydantic schemas (CR-016)."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class LifecycleStageResponse(BaseModel):
    """Response schema for user lifecycle stage."""
    user_id: str
    stage: str = Field(description="honeymoon/growth/regular/returnee")
    days_since_registration: int
    days_since_last_login: Optional[int] = None
    daily_base_quota: int


class QuotaStatusResponse(BaseModel):
    """Response schema for user quota status."""
    user_id: str
    date: date
    base_quota: int
    consumed: int
    fragment_extra: int
    fragment_consumed: int
    remaining: int = Field(description="Total remaining quota (base + fragment)")
    is_exempt: bool = Field(description="Whether user is exempt from quota")


class ConsumeQuotaResponse(BaseModel):
    """Response schema for quota consumption."""
    success: bool
    remaining: int
    message: Optional[str] = None


class AddFragmentQuotaRequest(BaseModel):
    """Request schema for adding fragment quota."""
    amount: int = Field(gt=0, description="Amount of fragment quota to add")


class QuotaResetResponse(BaseModel):
    """Response schema for daily quota reset."""
    reset_count: int
    reset_at: datetime
