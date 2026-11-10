"""
Phrase Schemas
==============
Pydantic models for saved / favourite phrases.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class PhraseCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    label: str | None = Field(default=None, max_length=100)
    language: str = Field(default="en", max_length=10)
    source: Literal["manual", "approved_message"] = "manual"


class PhraseUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=2000)
    label: str | None = None
    language: str | None = None


class PhraseResponse(BaseModel):
    id: str
    user_id: str
    text: str
    label: Optional[str] = None
    language: str
    source: str
    created_at: str
