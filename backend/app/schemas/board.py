"""
Board & Vocabulary Schemas
===========================
Pydantic models for boards and vocabulary tile endpoints.
"""

from typing import List, Literal
from pydantic import BaseModel, Field


# ── Board Schemas ─────────────────────────────────────────────────────────

class BoardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_default: bool = False
    categories: List[str] = Field(default_factory=list)


class BoardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    is_default: bool | None = None
    categories: List[str] | None = None


class BoardResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str | None
    is_default: bool
    categories: List[str]
    tile_count: int = 0
    created_at: str
    updated_at: str
