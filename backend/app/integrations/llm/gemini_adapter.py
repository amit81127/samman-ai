"""
Google Gemini Adapter — Samaan AI
==================================
Production-ready, resilient, quota-aware LLM adapter using the Google GenAI SDK (google-genai).
Integrates:
- Model Router: intelligent routing with configurable primary and fallback candidates.
- Circuit Breaker: short-lived protection against repeated 503/429 failures.
- Exponential Backoff with Jitter: structured retry logic for transient errors.
- Comprehensive Exception Handling: structured error logging without sensitive data leaks.
- Quota Manager: concurrency limits, sliding-window RPM, and daily RPD protection.
- Prometheus Telemetry: request count, durations, tokens, and fallback counters.
"""

import asyncio
import json
import logging
import random
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types

from app.core.config import settings
from app.ai.schemas.candidate import CandidateResult
from app.ai.generation.prompt_builder import PromptBuilder
from app.integrations.llm.model_router import model_router
from app.integrations.llm.quota_manager import quota_manager
from app.integrations.llm.circuit_breaker import circuit_breaker
from app.integrations.llm.metrics import llm_metrics

logger = logging.getLogger(__name__)


def _extract_error_details(exc: Exception) -> Dict[str, Any]:
    """
    Extracts structured, production-safe diagnostic details from any exception.
    Never exposes API keys or sensitive user information.
    """
    err_type = type(exc).__name__
    raw_str = str(exc)
    raw_repr = repr(exc)

    # 1. Extract HTTP status code
    status_code: Optional[int] = None
    if hasattr(exc, "code") and isinstance(exc.code, int):
        status_code = exc.code
    elif hasattr(exc, "status_code") and isinstance(exc.status_code, int):
        status_code = exc.status_code
    elif hasattr(exc, "http_status") and isinstance(exc.http_status, int):
        status_code = exc.http_status
    else:
        # Search in string representation e.g. "503 UNAVAILABLE" or "404 NOT_FOUND"
        match = re.search(r"\b(400|401|403|404|408|429|500|502|503|504)\b", f"{raw_str} {raw_repr}")
        if match:
            status_code = int(match.group(1))

    # 2. Extract clean error message
    message = None
    if hasattr(exc, "message") and exc.message:
        message = str(exc.message)
    elif raw_str and raw_str.strip():
        message = raw_str.strip()
    else:
        message = raw_repr if raw_repr.strip() else f"Unknown exception {err_type}"

    # 3. Redact any accidental API key patterns
    safe_message = re.sub(
        r"(AQ\.[A-Za-z0-9_-]{20,}|AIzaSy[A-Za-z0-9_-]{33})",
        "[REDACTED_API_KEY]",
        message,
    )

    # 4. Check for Retry-After header / delay hint
    retry_after: Optional[float] = None
    retry_match = re.search(r"retry[-_]after[:=]\s*(\d+(\.\d+)?)", safe_message, re.IGNORECASE)
    if retry_match:
        try:
            retry_after = float(retry_match.group(1))
        except ValueError:
            pass

    # 5. Determine retryability
    # Non-retryable: 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found / Model deprecated)
    # Retryable: 429 (Rate Limit), 500, 502, 503 (Unavailable), 504 (Gateway Timeout), Timeout, Connection
    is_retryable = False
    if status_code in (429, 500, 502, 503, 504):
        is_retryable = True
    elif isinstance(exc, (asyncio.TimeoutError, TimeoutError)) or "timeout" in safe_message.lower():
        is_retryable = True
    elif "connection" in safe_message.lower() or "unavailable" in safe_message.lower() or "high demand" in safe_message.lower():
        is_retryable = True

    return {
        "type": err_type,
        "status_code": status_code,
        "message": safe_message,
        "is_retryable": is_retryable,
        "retry_after": retry_after,
    }


def _compute_backoff_delay(
    attempt: int,
    base: float = 2.0,
    max_backoff: float = 15.0,
    retry_after: Optional[float] = None,
) -> float:
    """Computes exponential backoff with full jitter."""
    if retry_after is not None and retry_after > 0:
        return min(retry_after, max_backoff)
    # base * (2 ^ (attempt - 1)) + jitter
    delay = base * (2 ** (attempt - 1))
    jitter = random.uniform(0.1, 0.6)
    return min(delay + jitter, max_backoff)


class GeminiAdapter:
    """
    Intelligent, quota-protected Gemini adapter with circuit breaking and exponential backoff.
    """

    def __init__(self):
        self._api_key = settings.GEMINI_API_KEY
        self._prompt_builder = PromptBuilder()
        self._last_model_used = settings.GEMINI_PRIMARY_MODEL
        self._temperature = settings.GEMINI_TEMPERATURE
        self._max_tokens = settings.GEMINI_MAX_OUTPUT_TOKENS
        self._timeout_seconds = settings.GEMINI_TIMEOUT_SECONDS
        self._max_retries = getattr(settings, "GEMINI_MAX_RETRIES", 3)
        self._backoff_base = getattr(settings, "GEMINI_BACKOFF_BASE_SECONDS", 2.0)
        self._backoff_max = getattr(settings, "GEMINI_BACKOFF_MAX_SECONDS", 15.0)
        self._client: Optional[genai.Client] = None

        if self._api_key:
            timeout_ms = int(self._timeout_seconds * 1000)
            self._client = genai.Client(
                api_key=self._api_key,
                http_options=types.HttpOptions(timeout=timeout_ms),
            )

    @property
    def model_name(self) -> str:
        return self._last_model_used or settings.GEMINI_PRIMARY_MODEL

    @property
    def last_model_used(self) -> str:
        return self._last_model_used

    async def generate_candidates(
        self,
        concepts: List[str],
        language: str,
        manual_override: Optional[str] = None,
    ) -> List[CandidateResult]:
        """
        Generate candidates for AAC concept tiles using intelligent routing.
        """
        prompt = self._prompt_builder.build(concepts, language)
        candidates, model_used = await self.generate_with_routing(
            prompt=prompt,
            concepts=concepts,
            task_type="aac_composition",
            manual_override=manual_override,
        )
        self._last_model_used = model_used
        return candidates

    async def generate_with_routing(
        self,
        prompt: str,
        concepts: Optional[List[str]] = None,
        task_type: Optional[str] = "aac_composition",
        manual_override: Optional[str] = None,
    ) -> Tuple[List[CandidateResult], str]:
        """
        Executes request using ModelRouter decision, CircuitBreaker protection,
        QuotaManager reservation, and fallback execution across models.
        """
        if not self._client or not self._api_key:
            logger.warning("GEMINI_API_KEY is not configured. Returning empty candidates.")
            return [], "offline"

        # 1. Routing decision
        decision = await model_router.route(
            prompt=prompt,
            concepts=concepts,
            task_type=task_type,
            manual_override=manual_override,
        )
        llm_metrics.record_routing_decision(decision.model, decision.reason)

        candidate_models = [decision.model] + [
            m for m in decision.fallback_models if m != decision.model
        ]

        # 2. Iterate through candidate models (preferred -> fallbacks)
        for model_idx, model in enumerate(candidate_models):
            is_fallback = model_idx > 0
            if is_fallback:
                prev_model = candidate_models[model_idx - 1]
                logger.info("Attempting fallback from %s to %s", prev_model, model)
                llm_metrics.record_fallback(prev_model, model, "failover")

            # Check circuit breaker
            if not await circuit_breaker.can_attempt(model):
                circuit_status = await circuit_breaker.get_circuit_status(model)
                logger.info("Skipping model %s (circuit breaker is %s). Trying next fallback.", model, circuit_status)
                continue

            # Check and reserve quota slot
            reservation = await quota_manager.reserve(model)
            if not reservation.allowed:
                logger.warning(
                    "Model %s rejected by quota manager: %s. Trying next eligible model.",
                    model, reservation.reason,
                )
                llm_metrics.record_error(model, "quota_rejected")
                continue

            # Attempt model call with exponential backoff & jitter
            for attempt in range(1, self._max_retries + 1):
                start_time = time.time()
                try:
                    config = types.GenerateContentConfig(
                        temperature=self._temperature,
                        max_output_tokens=self._max_tokens,
                        response_mime_type="application/json",
                    )

                    response = await self._client.aio.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=config,
                    )

                    duration = time.time() - start_time
                    llm_metrics.record_duration(model, duration)
                    llm_metrics.increment_requests(model, "success")
                    await circuit_breaker.record_success(model)

                    # Record tokens if available
                    token_count = 0
                    if hasattr(response, "usage_metadata") and response.usage_metadata:
                        token_count = getattr(response.usage_metadata, "total_token_count", 0) or 0
                        p_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                        c_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                        llm_metrics.record_tokens(model, "prompt", p_tokens)
                        llm_metrics.record_tokens(model, "candidates", c_tokens)

                    await quota_manager.record_usage(model, tokens=token_count, success=True)

                    if response and response.text:
                        candidates = self._parse_structured_json(response.text)
                        if candidates:
                            self._last_model_used = model
                            logger.info(
                                "Gemini success with %s: %d candidates (%.2fs)",
                                model, len(candidates), duration,
                            )
                            return candidates, model

                    logger.warning("Gemini model %s returned empty text/candidates.", model)
                    break  # Break retry loop to try next fallback model if any

                except Exception as exc:
                    duration = time.time() - start_time
                    err_info = _extract_error_details(exc)
                    status_code = err_info["status_code"]
                    err_msg = err_info["message"]
                    err_type = err_info["type"]
                    is_retryable = err_info["is_retryable"]

                    logger.warning(
                        "Gemini %s attempt %d/%d failed (status=%s, type=%s, duration=%.2fs): %s",
                        model, attempt, self._max_retries, status_code, err_type, duration, err_msg,
                    )

                    # 401 / 403: Authentication or permission errors — do not retry, fatal for key
                    if status_code in (401, 403):
                        llm_metrics.record_error(model, "auth_error")
                        await quota_manager.record_usage(model, success=False)
                        logger.error("Authentication/Permission error calling Gemini %s: %s", model, err_msg)
                        return [], model

                    # 400: Invalid argument — do not retry
                    if status_code == 400:
                        llm_metrics.record_error(model, "invalid_argument")
                        await quota_manager.record_usage(model, success=False)
                        break

                    # 404: Model not found / deprecated — do not retry, trip circuit, failover immediately
                    if status_code == 404:
                        llm_metrics.record_error(model, "model_not_found_404")
                        await circuit_breaker.record_failure(model, is_severe=True)
                        await quota_manager.record_usage(model, success=False)
                        break

                    # 429: Rate limit or Quota exhausted
                    if status_code == 429 or "quota" in err_msg.lower() or "resource_exhausted" in err_msg.lower():
                        llm_metrics.record_error(model, "rate_limit_429")
                        await circuit_breaker.record_failure(model, is_severe=True)
                        await quota_manager.record_usage(model, success=False)
                        if attempt < self._max_retries and is_retryable:
                            delay = _compute_backoff_delay(attempt, self._backoff_base, self._backoff_max, err_info.get("retry_after"))
                            logger.info("Rate limit backoff: sleeping %.2fs before retry %d on %s", delay, attempt + 1, model)
                            await asyncio.sleep(delay)
                            continue
                        else:
                            break

                    # 500 / 502 / 503 / 504 / Timeouts: transient server errors
                    if is_retryable:
                        llm_metrics.record_error(model, "server_error_5xx")
                        await circuit_breaker.record_failure(model, is_severe=True)
                        if attempt < self._max_retries:
                            delay = _compute_backoff_delay(attempt, self._backoff_base, self._backoff_max, err_info.get("retry_after"))
                            logger.info("Transient 5xx/Timeout backoff: sleeping %.2fs before retry %d on %s", delay, attempt + 1, model)
                            await asyncio.sleep(delay)
                            continue
                        else:
                            await quota_manager.record_usage(model, success=False)
                            break

                    # Any other unclassified error
                    llm_metrics.record_error(model, "unknown_error")
                    await quota_manager.record_usage(model, success=False)
                    break

        logger.error("All candidate Gemini models exhausted (%s). Returning empty candidates.", candidate_models)
        return [], self._last_model_used

    def _parse_structured_json(self, raw_text: str) -> List[CandidateResult]:
        """
        Extracts, sanitizes, and validates candidate items from Gemini response text.
        Handles markdown fences, trailing commas, and partial JSON gracefully.
        """
        if not raw_text or not raw_text.strip():
            return []

        clean = raw_text.strip()

        # Remove markdown code blocks if wrapped
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]

        clean = clean.strip()

        # Attempt standard JSON parse
        try:
            data = json.loads(clean)
        except json.JSONDecodeError:
            # Fallback regex extraction if model returned surrounding text
            match = re.search(r"\{.*\}", clean, flags=re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                except json.JSONDecodeError:
                    logger.warning("Failed to decode JSON from Gemini response: %s", clean[:150])
                    return []
            else:
                logger.warning("No JSON object found in Gemini response: %s", clean[:150])
                return []

        if not isinstance(data, dict) or "candidates" not in data:
            logger.warning("Gemini JSON missing 'candidates' root array: %s", clean[:150])
            return []

        raw_candidates = data["candidates"]
        if not isinstance(raw_candidates, list):
            return []

        candidates = []
        for item in raw_candidates:
            if not isinstance(item, dict):
                continue
            text = item.get("text", "").strip()
            if not text:
                continue
            candidates.append(
                CandidateResult(
                    text=text,
                    preserved_concepts=item.get("preserved_concepts", []),
                    unsupported_additions=item.get("unsupported_additions", []),
                    requires_clarification=item.get("requires_clarification", False),
                )
            )

        return candidates
