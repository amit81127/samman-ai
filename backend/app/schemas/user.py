"""
User & Profile Schemas
======================
Request and response models for user profile endpoints.
"""

from typing import Literal
from pydantic import BaseModel


class ProfileResponse(BaseModel):
    """Full profile including accessibility preferences."""
    user_id: str
    language: str
    voice_preference: str | None = None
    gnani_api_key: str | None = None
    tile_size: Literal["small", "medium", "large"] = "medium"
    text_size: Literal["normal", "large", "xlarge"] = "normal"
    contrast_mode: bool = False
    reduced_motion: bool = False


class ProfileUpdate(BaseModel):
    """PATCH /profile — all fields optional."""
    language: str | None = None
    voice_preference: str | None = None
    gnani_api_key: str | None = None
    tile_size: Literal["small", "medium", "large"] | None = None
    text_size: Literal["normal", "large", "xlarge"] | None = None
    contrast_mode: bool | None = None
    reduced_motion: bool | None = None
