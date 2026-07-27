"""Subscription Pydantic schemas (CR-016)."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TierPermissions(BaseModel):
    """Permissions for a specific subscription tier."""
    archive_limit: int = Field(description="Maximum archives allowed")
    script_access: str = Field(description="trial_only/all_normal/all_including_exclusive")
    voice_enabled: bool = Field(description="Whether voice features are enabled")
    rewind_c15: bool = Field(description="Whether C15 rewind is enabled")
    ugc_access: bool = Field(description="Whether UGC features are accessible")
    fragment_discount: float = Field(description="Fragment purchase discount 0~1")
    hidden_options: bool = Field(description="Whether hidden dialogue options are shown")
    dialogue_limit: int = Field(description="Daily dialogue limit, -1=unlimited")


class SubscriptionResponse(BaseModel):
    """Response schema for subscription info."""
    id: str
    user_id: str
    tier: str
    status: str
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserTierResponse(BaseModel):
    """Response schema for user tier and permissions."""
    user_id: str
    tier: str
    status: str
    permissions: TierPermissions
    is_exempt_from_quota: bool = Field(description="Whether user is exempt from dynamic quota")


class PermissionCheckResponse(BaseModel):
    """Response schema for permission check."""
    user_id: str
    permission_name: str
    allowed: bool
    current_value: Optional[str] = None
