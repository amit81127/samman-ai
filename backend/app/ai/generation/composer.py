"""
AI Composer — Samaan AI
=======================
Orchestrates the full AI generation + validation pipeline.
Takes selected concepts, runs Gemini, validates candidates, and enforces safety guardrails.

CRITICAL INVARIANT:
When all Gemini models fail or validation fails, it NEVER returns an empty candidate list.
It activates a safe, verified literal candidate so the user can always communicate.
"""

import logging
from typing import Any, Dict, List, Tuple

from app.ai.schemas.candidate import CandidateResult
from app.ai.validation.concept_validator import validate_concepts
from app.ai.validation.negation_validator import validate_negation
from app.ai.validation.safety_validator import validate_safety
from app.core.cache import cache
from app.integrations.llm.gemini_adapter import GeminiAdapter

logger = logging.getLogger(__name__)


class AIComposer:
    """
    Runs: concepts → Gemini → concept validation → negation validation
           → safety validation → validated candidates
    """

    def __init__(self, llm: GeminiAdapter | None = None):
        self._llm = llm or GeminiAdapter()

    def build_literal(self, concepts: List[str]) -> str:
        """
        Create a deterministic literal message from selected concepts.
        This is always available regardless of AI or network status.
        """
        if not concepts:
            return ""
        return " ".join(concepts) + "."

    async def generate(
        self, concepts: List[str], language: str
    ) -> Tuple[str, List[dict], Dict[str, Any]]:
        """
        Generate and validate AI candidates.

        Returns:
            (literal_text, candidates, generation_metadata)
            - If AI succeeds: returns validated candidates + metadata
            - If AI fails or all models exhausted: returns literal candidate + fallback metadata
        """
        literal = self.build_literal(concepts)

        # 1. Check AI Generation Cache for instant 0ms response
        cache_key = f"llm:{language.strip().lower()}:{','.join(c.strip().lower() for c in concepts)}"
        cached = await cache.get(cache_key)
        if cached is not None:
            logger.info("AI Candidate Cache HIT for '%s' (0ms)", cache_key)
            return literal, cached, {
                "status": "ai_generated",
                "fallback_used": False,
                "model": "cache",
                "reason": "cache_hit",
            }

        # 2. Attempt AI generation if cache miss
        raw_candidates: List[CandidateResult] = []
        try:
            raw_candidates = await self._llm.generate_candidates(concepts, language)
        except Exception as exc:
            logger.warning("Error calling LLM adapter: %s", exc)
            raw_candidates = []

        validated: List[dict] = []
        if raw_candidates:
            for idx, candidate in enumerate(raw_candidates):
                candidate_id = f"c{idx + 1}"
                status = self._validate(candidate, concepts)
                validated.append({
                    "candidate_id": candidate_id,
                    "text": candidate.text,
                    "validation_status": status,
                    "requires_clarification": candidate.requires_clarification,
                    "model": self._llm.model_name,
                })

        passed_candidates = [c for c in validated if c["validation_status"] == "passed"]

        # 3. If models succeeded and at least one candidate passed validation
        if passed_candidates:
            logger.info(
                "AI generation success with model %s: %d/%d candidates passed",
                self._llm.model_name, len(passed_candidates), len(validated),
            )
            await cache.set(cache_key, validated, ttl=86400)
            return literal, validated, {
                "status": "ai_generated",
                "fallback_used": False,
                "model": self._llm.model_name,
                "reason": "model_success",
            }

        # 4. Critical Safe AAC Fallback: Never return an empty candidate list!
        reason = "all_models_unavailable" if not raw_candidates else "candidates_failed_validation"
        logger.warning(
            "Activating literal fallback for concepts %s (reason: %s).",
            concepts, reason,
        )

        literal_candidate = {
            "candidate_id": "c_literal",
            "text": literal,
            "validation_status": "passed",
            "requires_clarification": False,
            "model": "literal_fallback",
        }

        fallback_metadata = {
            "status": "fallback",
            "fallback_used": True,
            "model": None,
            "reason": reason,
        }

        return literal, [literal_candidate], fallback_metadata

    def _validate(self, candidate: CandidateResult, concepts: List[str]) -> str:
        """Run all three validators. Returns 'passed' or 'failed:<reason>'."""
        if not validate_concepts(candidate.text, concepts):
            return "failed:concept_missing"
        if not validate_negation(candidate.text, concepts):
            return "failed:negation_reversed"
        if not validate_safety(candidate.text, concepts, candidate.unsupported_additions):
            return "failed:safety_violation"
        return "passed"
