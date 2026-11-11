"""
Board & Vocabulary Schemas
===========================
Pydantic models for boards and vocabulary tile endpoints.
"""

from datetime import datetime
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


# ── Board Schemas ─────────────────────────────────────────────────────────

class BoardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_default: bool = False
    categories: List[str] = Field(default_factory=list)


class BoardUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_default: Optional[bool] = None
    categories: Optional[List[str]] = None


class BoardResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    is_default: bool = False
    categories: List[str] = Field(default_factory=list)
    tile_count: int = 0
    created_at: Union[str, datetime] = ""
    updated_at: Union[str, datetime] = ""
