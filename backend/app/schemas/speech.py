"""
Speech Schemas
==============
Request and response models for TTS endpoints.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class SpeechSynthesizeRequest(BaseModel):
    """Optional customization parameters when synthesizing an approved message."""
    language: Optional[str] = Field(default=None, description="Language code e.g. en-IN, hi-IN, kn-IN, ta-IN")
    voice: Optional[str] = Field(default=None, description="Gnani voice persona e.g. Shivani, Prakash, Lakshmi")
    api_key: Optional[str] = Field(default=None, description="Custom Gnani AI API key for this user")


class DirectSynthesizeRequest(BaseModel):
    """Direct speech synthesis for phrases or quick text."""
    text: str = Field(min_length=1, max_length=1000, description="Text to synthesize")
    language: Optional[str] = Field(default=None, description="Language code e.g. en-IN, hi-IN, kn-IN, ta-IN")
    voice: Optional[str] = Field(default=None, description="Gnani voice persona e.g. Shivani, Prakash, Lakshmi")
    api_key: Optional[str] = Field(default=None, description="Custom Gnani AI API key for this user")


class SpeechJobResponse(BaseModel):
    """Status of a TTS synthesis job."""
    job_id: str
    message_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    audio_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
