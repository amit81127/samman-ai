"""
Circuit Breaker for LLM Models — Samaan AI
==========================================
Protects the system from hammering overloaded or failing models (503 / 429).
Automatically routes traffic to healthy fallback models and handles self-healing.
"""

import asyncio
from enum import Enum
import logging
import time
from typing import Dict

from app.core.config import settings

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"        # Normal: calls allowed
    OPEN = "open"            # Tripped: fast-fail, skip to fallback
    HALF_OPEN = "half_open"  # Probe: testing if model has recovered


class ModelCircuitState:
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 30.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.consecutive_failures: int = 0
        self.total_requests: int = 0
        self.total_failures: int = 0
        self.state: CircuitState = CircuitState.CLOSED
        self.last_state_change: float = time.time()
        self.last_failure_time: float = 0.0

    def can_attempt(self) -> bool:
        """Check if request can be sent to this model."""
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if cooldown has elapsed
            if now - self.last_state_change >= self.cooldown_seconds:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                logger.info("Circuit for model moved to HALF_OPEN (probing recovery)")
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            # Allow trial request
            return True

        return True

    def record_success(self) -> None:
        """Record a successful response."""
        self.total_requests += 1
        self.consecutive_failures = 0
        if self.state in (CircuitState.HALF_OPEN, CircuitState.OPEN):
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()
            logger.info("Circuit breaker recovered: model is now CLOSED (healthy)")

    def record_failure(self, is_severe: bool = True) -> None:
        """Record an error (e.g. 503, 429, timeout)."""
        now = time.time()
        self.total_requests += 1
        self.total_failures += 1
        self.consecutive_failures += 1
        self.last_failure_time = now

        if not is_severe:
            return

        if self.state == CircuitState.HALF_OPEN:
            # Trial failed, trip back to OPEN
            self.state = CircuitState.OPEN
            self.last_state_change = now
            logger.warning("Circuit breaker probe failed: model remains OPEN for %ds", int(self.cooldown_seconds))
        elif self.state == CircuitState.CLOSED and self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = now
            logger.warning(
                "Circuit breaker tripped for model (consecutive_failures=%d >= threshold=%d). Model OPEN for %ds",
                self.consecutive_failures,
                self.failure_threshold,
                int(self.cooldown_seconds),
            )


class CircuitBreakerManager:
    """Manages circuit breakers across all configured Gemini models."""

    def __init__(self):
        self._states: Dict[str, ModelCircuitState] = {}
        self._lock = asyncio.Lock()

    def _get_state(self, model: str) -> ModelCircuitState:
        if model not in self._states:
            threshold = getattr(settings, "GEMINI_CIRCUIT_BREAKER_FAILURE_THRESHOLD", 3)
            cooldown = float(getattr(settings, "GEMINI_CIRCUIT_BREAKER_COOLDOWN", 30))
            self._states[model] = ModelCircuitState(failure_threshold=threshold, cooldown_seconds=cooldown)
        return self._states[model]

    async def can_attempt(self, model: str) -> bool:
        """Returns True if the circuit allows calling this model."""
        if not getattr(settings, "GEMINI_CIRCUIT_BREAKER_ENABLED", True):
            return True
        async with self._lock:
            return self._get_state(model).can_attempt()

    async def record_success(self, model: str) -> None:
        async with self._lock:
            self._get_state(model).record_success()

    async def record_failure(self, model: str, is_severe: bool = True) -> None:
        async with self._lock:
            self._get_state(model).record_failure(is_severe=is_severe)

    async def get_circuit_status(self, model: str) -> str:
        async with self._lock:
            return self._get_state(model).state.value

    async def reset(self, model: str) -> None:
        async with self._lock:
            if model in self._states:
                del self._states[model]


circuit_breaker = CircuitBreakerManager()

