"""Scene config Pydantic schemas (CR-027)."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class SceneConfigUpsert(BaseModel):
    """Create or update scene config request."""
    scene_name: str = Field(..., min_length=1, max_length=200)
    tags: List[str] = Field(default_factory=list, max_length=20)
    description: Optional[str] = Field(None, max_length=5000)


class SceneConfigResponse(BaseModel):
    """Scene config response."""
    id: str
    node_id: str
    scene_name: str
    tags: List[str]
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('id', 'node_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        return str(v) if isinstance(v, UUID) else v
