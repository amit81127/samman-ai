"""
Lightweight In-Process Background Tasks
=======================================
Helper functions intended ONLY for non-critical, fire-and-forget operations
using FastAPI's BackgroundTasks (e.g. audit metric logging, telemetry,
ephemeral cache invalidation).

DURABLE or CRITICAL workloads (like Speech Synthesis, retryable syncs, or
scheduled maintenance) MUST use the MongoDB-backed JobRepository and JobWorker.
"""

import logging
from typing import Any, Dict

from app.core.cache import cache

logger = logging.getLogger("samaan.lightweight_tasks")


async def record_access_audit_event(
    event_name: str,
    user_id: str,
    metadata: Dict[str, Any],
) -> None:
    """Non-blocking fire-and-forget audit metric logging."""
    logger.debug("Audit event [%s] for user %s: %s", event_name, user_id, metadata)


async def fire_and_forget_cache_invalidation(namespace: str, key: str) -> None:
    """Non-blocking cache key invalidation following mutation responses."""
    try:
        await cache.cache_delete(namespace, key)
    except Exception as exc:
        logger.warning("Fire-and-forget cache eviction error: %s", exc)


async def record_usage_metric(metric_name: str, value: float = 1.0) -> None:
    """Non-blocking usage metric increment."""
    logger.debug("Metric recorded: %s = %.2f", metric_name, value)

