"""
AI Candidate Schemas
=====================
Internal Pydantic models for structured Gemini output.
These are INTERNAL schemas — not returned to the frontend directly.
"""

from typing import List
from pydantic import BaseModel


class CandidateResult(BaseModel):
    """A single sentence candidate returned by the LLM."""
    text: str
    preserved_concepts: List[str] = []
    unsupported_additions: List[str] = []
    requires_clarification: bool = False


class GeminiResponse(BaseModel):
    """Expected JSON structure from Gemini API."""
    candidates: List[CandidateResult]
