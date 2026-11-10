"""
Vocabulary Item Schemas
========================
Pydantic models for vocabulary tile endpoints.
"""

from pydantic import BaseModel, Field


class VocabItemCreate(BaseModel):
    label: str = Field(min_length=1, max_length=100)
    symbol_uri: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=100)
    position: int = Field(default=0, ge=0)
    color: str | None = Field(default=None, max_length=7)  # hex e.g. #FF5733


class VocabItemUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=100)
    symbol_uri: str | None = None
    category: str | None = None
    position: int | None = Field(default=None, ge=0)
    color: str | None = None


class VocabItemResponse(BaseModel):
    id: str
    board_id: str
    user_id: str
    label: str
    symbol_uri: str | None
    category: str | None
    position: int
    color: str | None
    is_active: bool
