"""
LLM Provider Base Interface
============================
Protocol-based interface that all LLM adapters must implement.
This keeps the application decoupled from any specific AI vendor.
"""

from typing import Protocol, List
from app.ai.schemas.candidate import CandidateResult


class LLMProvider(Protocol):
    """
    Interface for LLM-based sentence generation.
    Any class implementing this protocol can be used as the AI backend.
    """
    async def generate_candidates(
        self,
        concepts: List[str],
        language: str,
    ) -> List[CandidateResult]:
        """
        Generate sentence candidates from a list of user-selected concepts.

        Args:
            concepts: Ordered list of concept labels e.g. ["I", "not", "want", "medicine"]
            language: BCP 47 language tag e.g. "en", "hi", "kn"

        Returns:
            List of CandidateResult objects — may be empty if generation fails.
        """
        ...
