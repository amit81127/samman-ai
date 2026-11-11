"""
Message Schemas
===============
Request and response models for message composition and retrieval.
"""

from datetime import datetime
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


class ConceptItem(BaseModel):
    """A single selected concept from the AAC board."""
    id: str
    label: str
    position: int


class ComposeRequest(BaseModel):
    """Body for POST /messages/compose"""
    selected_concepts: List[ConceptItem] = Field(min_length=1)
    request_ai_suggestions: bool = True


class CandidateInResponse(BaseModel):
    """An AI or literal candidate as shown to the user."""
    candidate_id: str
    text: str
    validation_status: str
    requires_clarification: bool = False
    model: Optional[str] = None


class GenerationMetadata(BaseModel):
    """Observability metadata about how the candidate was formed."""
    status: Literal["ai_generated", "fallback", "literal_only"] = "ai_generated"
    fallback_used: bool = False
    model: Optional[str] = None
    reason: Optional[str] = None


class MessageResponse(BaseModel):
    """Full message with literal text and candidates."""
    id: str
    user_id: str
    selected_concepts: List[ConceptItem]
    literal_text: str
    candidates: List[CandidateInResponse]
    model: Optional[str] = None
    generation: Optional[GenerationMetadata] = None
    approved_text: Optional[str] = None
    approval_status: Literal["pending", "approved", "expired"] = "pending"
    version: int = 0
    created_at: Union[str, datetime] = ""
    updated_at: Union[str, datetime] = ""
