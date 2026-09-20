"""Lorebook Pydantic schemas (CR-027)."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union
from datetime import datetime
from uuid import UUID


class LorebookEntryCreate(BaseModel):
    """Create lorebook entry request."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=5000)
    tags: List[str] = Field(default_factory=list, max_length=20)
    priority: int = Field(default=0, ge=0)

    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        for tag in v:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' exceeds 50 chars")
        return v


class LorebookEntryUpdate(BaseModel):
    """Update lorebook entry request."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    tags: Optional[List[str]] = Field(None, max_length=20)
    priority: Optional[int] = Field(None, ge=0)


class LorebookEntryResponse(BaseModel):
    """Lorebook entry response."""
    id: str
    title: str
    content: str
    tags: List[str]
    priority: int
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('id', 'created_by', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        return str(v) if isinstance(v, UUID) else v


class LorebookEntryListItem(BaseModel):
    """Lorebook entry list item (no content)."""
    id: str
    title: str
    tags: List[str]
    priority: int
    status: str
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        return str(v) if isinstance(v, UUID) else v


class LorebookEntryListResponse(BaseModel):
    """Paginated lorebook entry list."""
    items: List[LorebookEntryListItem]
    total: int
    page: int
    page_size: int
