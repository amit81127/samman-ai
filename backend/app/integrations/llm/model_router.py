"""
Intelligent Model Router — Samaan AI
====================================
Determines optimal Gemini model for incoming requests:
- Primary: gemini-3.5-flash-lite (high-volume, everyday AAC, conversations, translations)
- Advanced: gemini-3.8-flash (multi-step reasoning, complex coding, deep analysis)
- Fallback chain: configurable via GEMINI_FALLBACK_MODELS

Features:
- Deterministic rule matching & lightweight complexity scoring without external LLM calls.
- Circuit breaker awareness: fast-fails temporarily overloaded/503 models.
- Quota-aware: falls back automatically if daily limits or RPM are exceeded.
"""

import logging
import re
from typing import List, Optional

from pydantic import BaseModel

from app.core.config import settings
from app.integrations.llm.quota_manager import quota_manager
from app.integrations.llm.circuit_breaker import circuit_breaker

logger = logging.getLogger(__name__)

# Keywords signaling advanced analytical / complex reasoning requirements
COMPLEXITY_KEYWORDS = {
    "step-by-step", "multi-step", "reasoning", "prove", "proof", "derivation",
    "architecture", "architect", "algorithm", "data structure", "optimization",
    "debug", "stack trace", "refactor", "diagnose", "complex", "deep dive",
    "comprehensive analysis", "trade-offs", "evaluate pros and cons",
    "mathematical", "differential", "theorem", "root cause", "explain why",
}

# Threshold above which a task is considered complex (0.0 to 1.0)
COMPLEXITY_THRESHOLD = 0.60


class RoutingDecision(BaseModel):
    """Encapsulates the model selection and reasoning."""
    model: str
    reason: str
    complexity_score: float
    is_override: bool = False
    fallback_models: List[str] = []


class ModelRouter:
    """Intelligently routes requests to Flash Lite or Advanced model."""

    def __init__(self):
        self.primary_model = settings.GEMINI_PRIMARY_MODEL
        self.advanced_model = settings.GEMINI_ADVANCED_MODEL
        self.fallback_model = settings.GEMINI_FALLBACK_MODEL
        self.smart_routing_enabled = settings.GEMINI_ENABLE_SMART_ROUTING
        self.fallback_enabled = settings.GEMINI_ENABLE_FALLBACK

    def get_configured_fallbacks(self) -> List[str]:
        """Return the ordered list of fallback models from configuration."""
        raw = getattr(settings, "GEMINI_FALLBACK_MODELS", "")
        if raw:
            models = [m.strip() for m in raw.split(",") if m.strip()]
            if models:
                return models
        return [self.fallback_model, "gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-3.6-flash"]

    def calculate_complexity(
        self,
        prompt: str,
        concepts: Optional[List[str]] = None,
        task_type: Optional[str] = None,
    ) -> float:
        """
        Compute a lightweight complexity score between 0.0 and 1.0.
        Uses prompt structure, length, keywords, and domain signals.
        """
        # AAC simple tile concept selection is strictly low complexity
        if task_type == "aac_composition" or (concepts and len(concepts) <= 6 and len(prompt) < 200):
            return 0.1

        score = 0.0
        text_lower = prompt.lower()

        # 1. Keyword density
        matches = [kw for kw in COMPLEXITY_KEYWORDS if kw in text_lower]
        score += min(len(matches) * 0.25, 0.6)

        # 2. Length / verbosity signal
        word_count = len(re.findall(r"\b\w+\b", prompt))
        if word_count > 300:
            score += 0.3
        elif word_count > 150:
            score += 0.15

        # 3. Code or structural syntax indicators
        if "```" in prompt or "def " in prompt or "class " in prompt or "{" in prompt and "}" in prompt:
            score += 0.25

        # 4. Multi-question / numbered lists
        numbered_items = len(re.findall(r"^\s*\d+[\.\)]\s+", prompt, flags=re.MULTILINE))
        if numbered_items >= 3:
            score += 0.2

        return min(round(score, 2), 1.0)

    async def route(
        self,
        prompt: str,
        concepts: Optional[List[str]] = None,
        task_type: Optional[str] = None,
        manual_override: Optional[str] = None,
    ) -> RoutingDecision:
        """
        Select the best model based on manual override, complexity, quota, and circuit breaker status.
        """
        configured_fallbacks = self.get_configured_fallbacks()

        # 1. Manual override check
        if manual_override:
            logger.info("Model routing: manual override specified -> %s", manual_override)
            fallbacks = [m for m in [self.primary_model] + configured_fallbacks if m != manual_override]
            return RoutingDecision(
                model=manual_override,
                reason="manual_override",
                complexity_score=0.5,
                is_override=True,
                fallback_models=fallbacks if self.fallback_enabled else [],
            )

        # 2. If smart routing is disabled, use configured primary
        if not self.smart_routing_enabled:
            fallbacks = [m for m in configured_fallbacks if m != self.primary_model]
            return RoutingDecision(
                model=self.primary_model,
                reason="smart_routing_disabled_default_primary",
                complexity_score=0.0,
                fallback_models=fallbacks if self.fallback_enabled else [],
            )

        # 3. Compute complexity
        score = self.calculate_complexity(prompt, concepts, task_type)

        # 4. Determine preferred model
        if score >= COMPLEXITY_THRESHOLD:
            preferred_model = self.advanced_model
            reason = f"complex_task_score_{score}"
        else:
            preferred_model = self.primary_model
            reason = f"standard_task_score_{score}"

        # 5. Quota check: if preferred is advanced model but daily/RPM quota exhausted, fall back to Lite
        if preferred_model == self.advanced_model:
            status = await quota_manager.get_quota_status()
            adv_status = status.get(self.advanced_model, {})
            if adv_status.get("rpd_remaining", 1) <= 0 or adv_status.get("rpm_remaining", 1) <= 0:
                logger.warning(
                    "Advanced model quota exhausted (%s). Downgrading to primary model %s",
                    adv_status, self.primary_model,
                )
                preferred_model = self.primary_model
                reason = "advanced_quota_exhausted_fallback_to_lite"

        # 6. Circuit breaker check: if preferred model is OPEN, select healthy alternative
        all_candidates = [preferred_model] + [m for m in configured_fallbacks if m != preferred_model]
        chosen_model = preferred_model
        for cand in all_candidates:
            if await circuit_breaker.can_attempt(cand):
                chosen_model = cand
                if cand != preferred_model:
                    reason = f"circuit_open_{preferred_model}_selected_{cand}"
                    logger.info("Model %s circuit is open, routed to %s", preferred_model, cand)
                break

        # 7. Build fallback chain excluding chosen model
        fallbacks = [m for m in all_candidates if m != chosen_model] if self.fallback_enabled else []

        logger.info(
            "Routing decision: model=%s, reason=%s, score=%.2f, fallbacks=%s",
            chosen_model, reason, score, fallbacks,
        )

        return RoutingDecision(
            model=chosen_model,
            reason=reason,
            complexity_score=score,
            is_override=False,
            fallback_models=fallbacks,
        )


# Global router instance
model_router = ModelRouter()
