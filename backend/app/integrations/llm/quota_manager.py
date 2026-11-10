"""
Quota Manager — Gemini AI Free Tier Protection
==============================================
Production-ready, concurrency-safe quota tracker and rate-limiter for Gemini models.
Enforces conservative application safety limits for:
- Requests Per Minute (RPM)
- Requests Per Day (RPD)
- Concurrent in-flight requests
- Token usage tracking

Supports automatic daily resets aligned to the configured timezone (e.g. Asia/Kolkata).
"""

import asyncio
import logging
import time
from collections import deque
from datetime import datetime
from typing import Dict, Optional, Tuple
from zoneinfo import ZoneInfo

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelQuotaConfig:
    """Holds safety limits for a specific Gemini model."""

    def __init__(self, rpm_limit: int, rpd_limit: int, max_concurrency: int = 2):
        self.rpm_limit = rpm_limit
        self.rpd_limit = rpd_limit
        self.max_concurrency = max_concurrency


class ReservationResult:
    """Result returned by reserve()."""
    def __init__(self, allowed: bool, reason: str):
        self.allowed = allowed
        self.reason = reason


class QuotaManager:
    """
    Tracks and enforces quota safety limits across models.
    Supports in-flight reservation, sliding window RPM, and daily RPD reset.
    """

    def __init__(self):
        self._tz = ZoneInfo(settings.GEMINI_QUOTA_TIMEZONE)
        self._lock = asyncio.Lock()

        # Build model-specific limits based on configuration
        self._configs: Dict[str, ModelQuotaConfig] = {
            settings.GEMINI_PRIMARY_MODEL: ModelQuotaConfig(
                rpm_limit=settings.GEMINI_LITE_RPM_LIMIT,
                rpd_limit=settings.GEMINI_LITE_DAILY_LIMIT,
                max_concurrency=4,
            ),
            settings.GEMINI_FALLBACK_MODEL: ModelQuotaConfig(
                rpm_limit=settings.GEMINI_LITE_RPM_LIMIT,
                rpd_limit=settings.GEMINI_LITE_DAILY_LIMIT,
                max_concurrency=4,
            ),
            settings.GEMINI_ADVANCED_MODEL: ModelQuotaConfig(
                rpm_limit=settings.GEMINI_ADVANCED_RPM_LIMIT,
                rpd_limit=settings.GEMINI_ADVANCED_DAILY_LIMIT,
                max_concurrency=2,
            ),
        }

        # In-memory tracking state:
        # sliding window timestamps for RPM (60s window)
        self._request_timestamps: Dict[str, deque] = {}
        # daily request count per model
        self._daily_requests: Dict[str, int] = {}
        # daily total tokens per model
        self._daily_tokens: Dict[str, int] = {}
        # active in-flight requests count
        self._active_requests: Dict[str, int] = {}
        # concurrency semaphores per model
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        # current date tracker for daily reset (YYYY-MM-DD)
        self._current_date_str = self._get_current_date()

    def _get_current_date(self) -> str:
        """Return current date string (YYYY-MM-DD) in configured timezone."""
        return datetime.now(self._tz).strftime("%Y-%m-%d")

    def _get_config(self, model: str) -> ModelQuotaConfig:
        """Lookup or infer quota config for a given model identifier."""
        if model in self._configs:
            return self._configs[model]
        # Infer conservative defaults if model is unknown
        if "lite" in model.lower():
            return ModelQuotaConfig(
                rpm_limit=settings.GEMINI_LITE_RPM_LIMIT,
                rpd_limit=settings.GEMINI_LITE_DAILY_LIMIT,
                max_concurrency=3,
            )
        return ModelQuotaConfig(
            rpm_limit=settings.GEMINI_ADVANCED_RPM_LIMIT,
            rpd_limit=settings.GEMINI_ADVANCED_DAILY_LIMIT,
            max_concurrency=2,
        )

    def _get_semaphore(self, model: str) -> asyncio.Semaphore:
        if model not in self._semaphores:
            cfg = self._get_config(model)
            self._semaphores[model] = asyncio.Semaphore(cfg.max_concurrency)
        return self._semaphores[model]

    def _check_and_apply_daily_reset(self) -> None:
        """Reset daily counters if date has changed in target timezone."""
        today = self._get_current_date()
        if today != self._current_date_str:
            logger.info("Resetting daily Gemini quotas for new day: %s (was %s)", today, self._current_date_str)
            self._daily_requests.clear()
            self._daily_tokens.clear()
            self._current_date_str = today

    async def check_and_reserve(self, model: str) -> Tuple[bool, str]:
        """
        Check if model has available quota and reserve a slot.
        Returns: (is_allowed: bool, reason: str)
        """
        async with self._lock:
            self._check_and_apply_daily_reset()
            cfg = self._get_config(model)
            now = time.time()

            # 1. Clean up old timestamps from sliding 60s window
            if model not in self._request_timestamps:
                self._request_timestamps[model] = deque()
            q = self._request_timestamps[model]
            while q and now - q[0] > 60.0:
                q.popleft()

            # 2. Check Daily Limit (RPD)
            current_rpd = self._daily_requests.get(model, 0)
            if current_rpd >= cfg.rpd_limit:
                logger.warning("Quota blocked: Model %s reached daily limit (%d/%d)", model, current_rpd, cfg.rpd_limit)
                return False, f"RPD_LIMIT_EXCEEDED ({current_rpd}/{cfg.rpd_limit})"

            # 3. Check Minute Limit (RPM) including in-flight reservations
            current_rpm = len(q)
            if current_rpm >= cfg.rpm_limit:
                wait_seconds = int(60.0 - (now - q[0])) + 1 if q else 1
                logger.warning("Quota blocked: Model %s reached RPM limit (%d/%d), wait ~%ds", model, current_rpm, cfg.rpm_limit, wait_seconds)
                return False, f"RPM_LIMIT_EXCEEDED (wait {wait_seconds}s)"

            # 4. Check Concurrency
            active = self._active_requests.get(model, 0)
            if active >= cfg.max_concurrency:
                logger.warning("Quota blocked: Model %s reached max concurrency (%d/%d)", model, active, cfg.max_concurrency)
                return False, f"CONCURRENCY_LIMIT_EXCEEDED ({active}/{cfg.max_concurrency})"

            # 5. Reserve slot
            q.append(now)
            self._daily_requests[model] = current_rpd + 1
            self._active_requests[model] = active + 1

            return True, "OK"

    async def reserve(self, model: str) -> ReservationResult:
        """Reserve a request slot for a model."""
        allowed, reason = await self.check_and_reserve(model)
        return ReservationResult(allowed=allowed, reason=reason)

    async def record_usage(
        self,
        model: str,
        tokens: int = 0,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """Record the outcome of a Gemini API request."""
        async with self._lock:
            # Decrement active in-flight count
            if model in self._active_requests and self._active_requests[model] > 0:
                self._active_requests[model] -= 1

            if success:
                self._daily_tokens[model] = self._daily_tokens.get(model, 0) + tokens
                logger.debug(
                    "Recorded Gemini usage for %s: success=True, tokens=%d, total_today=%d",
                    model, tokens, self._daily_tokens[model],
                )
            else:
                logger.debug("Recorded Gemini failure for %s: error=%s", model, error)
                # If the error was a client validation failure (e.g. 400), don't penalize daily quota unnecessarily
                if error and "400" in error and model in self._daily_requests:
                    self._daily_requests[model] = max(0, self._daily_requests[model] - 1)

    async def get_quota_status(self) -> Dict[str, dict]:
        """Return snapshot of current quota usage across all registered models."""
        async with self._lock:
            self._check_and_apply_daily_reset()
            now = time.time()
            status = {}

            all_models = set(self._configs.keys()) | set(self._daily_requests.keys())
            for model in all_models:
                cfg = self._get_config(model)
                q = self._request_timestamps.get(model, deque())
                # Active timestamps in last 60s
                active_rpm = sum(1 for ts in q if now - ts <= 60.0)
                used_rpd = self._daily_requests.get(model, 0)
                used_tokens = self._daily_tokens.get(model, 0)
                active_in_flight = self._active_requests.get(model, 0)

                status[model] = {
                    "rpm_used": active_rpm,
                    "rpm_limit": cfg.rpm_limit,
                    "rpm_remaining": max(0, cfg.rpm_limit - active_rpm),
                    "rpd_used": used_rpd,
                    "rpd_limit": cfg.rpd_limit,
                    "rpd_remaining": max(0, cfg.rpd_limit - used_rpd),
                    "active_concurrency": active_in_flight,
                    "max_concurrency": cfg.max_concurrency,
                    "total_tokens_today": used_tokens,
                    "date": self._current_date_str,
                    "timezone": str(self._tz),
                }
            return status

    async def force_daily_reset(self) -> None:
        """Manually reset daily quotas (useful for testing or admin tools)."""
        async with self._lock:
            self._daily_requests.clear()
            self._daily_tokens.clear()
            self._current_date_str = self._get_current_date()
            logger.info("Forced daily quota reset completed.")


# Global quota manager instance
quota_manager = QuotaManager()
