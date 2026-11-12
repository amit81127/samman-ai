"""
SAMAAN AI — Production Observability & Monitoring Engine
========================================================
Comprehensive system metrics collector:
- API latency percentiles: P50, P90, P95, P99
- HTTP error rates & status code distribution (2xx, 4xx, 5xx)
- MongoDB query latency tracking
- Gemini AI generation & Gnani Timbre TTS latency tracking
- Process CPU & Memory (RSS, Virtual) utilization via psutil
- Two-level Cache (L1 Memory + L2 Disk) hit/miss ratios
- HTTP Connection Pool utilization
- Optional Sentry exception monitoring integration
- Prometheus scrape exposition format
"""

import logging
import os
import threading
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import psutil

from app.core.config import settings
from app.core.cache import cache

logger = logging.getLogger("samaan.monitoring")


class RollingWindowMetrics:
    """Thread-safe circular buffer for recording latencies and calculating percentiles."""

    def __init__(self, max_samples: int = 2000):
        self._max_samples = max_samples
        self._samples: List[float] = []
        self._lock = threading.Lock()

    def record(self, value: float) -> None:
        with self._lock:
            self._samples.append(value)
            if len(self._samples) > self._max_samples:
                self._samples.pop(0)

    def get_percentiles(self) -> Dict[str, float]:
        with self._lock:
            if not self._samples:
                return {"p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0, "min": 0.0, "max": 0.0, "count": 0}
            sorted_samples = sorted(self._samples)
            n = len(sorted_samples)

            def _pct(p: float) -> float:
                idx = min(int(n * p), n - 1)
                return round(sorted_samples[idx], 2)

            return {
                "p50": _pct(0.50),
                "p90": _pct(0.90),
                "p95": _pct(0.95),
                "p99": _pct(0.99),
                "avg": round(sum(sorted_samples) / n, 2),
                "min": round(sorted_samples[0], 2),
                "max": round(sorted_samples[-1], 2),
                "count": n,
            }


class SystemMetricsCollector:
    """Central singleton telemetry collector for the entire backend application."""

    def __init__(self):
        self._lock = threading.Lock()
        self._start_time = time.time()

        # Latency windows
        self._api_latency = RollingWindowMetrics(max_samples=5000)
        self._endpoint_latencies: Dict[str, RollingWindowMetrics] = defaultdict(lambda: RollingWindowMetrics(max_samples=1000))
        self._mongo_latency = RollingWindowMetrics(max_samples=2000)
        self._gemini_latency = RollingWindowMetrics(max_samples=1000)
        self._gnani_tts_latency = RollingWindowMetrics(max_samples=1000)

        # HTTP counters: (method, status_code) -> count
        self._http_requests_total = 0
        self._http_errors_2xx = 0
        self._http_errors_4xx = 0
        self._http_errors_5xx = 0
        self._status_counters: Dict[int, int] = defaultdict(int)

        # Process reference for psutil
        try:
            self._process = psutil.Process(os.getpid())
            # Prime CPU percent measurement
            self._process.cpu_percent()
        except Exception:
            self._process = None

        self._init_sentry()

    def _init_sentry(self) -> None:
        """Initialize Sentry SDK if SENTRY_DSN is configured in settings or environment."""
        sentry_dsn = getattr(settings, "SENTRY_DSN", None) or os.getenv("SENTRY_DSN")
        if sentry_dsn:
            try:
                import sentry_sdk
                from sentry_sdk.integrations.fastapi import FastApiIntegration
                from sentry_sdk.integrations.pymongo import PyMongoIntegration

                sentry_sdk.init(
                    dsn=sentry_dsn,
                    environment=settings.APP_ENV,
                    traces_sample_rate=0.2 if settings.is_production else 1.0,
                    integrations=[FastApiIntegration(), PyMongoIntegration()],
                )
                logger.info("Sentry monitoring initialized successfully")
            except Exception as exc:
                logger.warning("Failed to initialize Sentry: %s", exc)

    # ── Record Instrumentation ──────────────────────────────────────────────

    def record_api_request(self, method: str, path: str, status_code: int, duration_ms: float) -> None:
        """Record an incoming HTTP request."""
        with self._lock:
            self._http_requests_total += 1
            self._status_counters[status_code] += 1
            if 200 <= status_code < 300:
                self._http_errors_2xx += 1
            elif 400 <= status_code < 500:
                self._http_errors_4xx += 1
            elif status_code >= 500:
                self._http_errors_5xx += 1

        self._api_latency.record(duration_ms)
        endpoint_key = f"{method} {path}"
        self._endpoint_latencies[endpoint_key].record(duration_ms)

    def record_mongo_query(self, duration_ms: float) -> None:
        """Record MongoDB query execution duration."""
        self._mongo_latency.record(duration_ms)

    def record_gemini_call(self, duration_ms: float) -> None:
        """Record Gemini LLM call duration."""
        self._gemini_latency.record(duration_ms)

    def record_gnani_tts_call(self, duration_ms: float) -> None:
        """Record Gnani AI Timbre TTS synthesis duration."""
        self._gnani_tts_latency.record(duration_ms)

    # ── Diagnostics & Telemetry Data ────────────────────────────────────────

    def get_system_metrics(self) -> Dict[str, Any]:
        """Aggregate all runtime health, performance, and resource usage metrics."""
        # 1. CPU & Memory
        cpu_pct = 0.0
        memory_mb = 0.0
        memory_pct = 0.0
        thread_count = 0
        if self._process:
            try:
                cpu_pct = self._process.cpu_percent()
                mem_info = self._process.memory_info()
                memory_mb = round(mem_info.rss / (1024 * 1024), 2)
                memory_pct = round(self._process.memory_percent(), 2)
                thread_count = self._process.num_threads()
            except Exception:
                pass

        # 2. HTTP Error Rates
        with self._lock:
            total_reqs = self._http_requests_total
            err_4xx = self._http_errors_4xx
            err_5xx = self._http_errors_5xx
            status_dist = dict(self._status_counters)

        error_rate_pct = round(((err_4xx + err_5xx) / total_reqs * 100), 2) if total_reqs > 0 else 0.0

        # 3. Latencies
        api_lat = self._api_latency.get_percentiles()
        mongo_lat = self._mongo_latency.get_percentiles()
        gemini_lat = self._gemini_latency.get_percentiles()
        gnani_lat = self._gnani_tts_latency.get_percentiles()

        # 4. Cache Statistics
        cache_stats = cache.get_stats()

        # 5. Connection Pool Utilization
        pool_stats = {
            "min_pool_size": settings.MONGODB_MIN_POOL_SIZE,
            "max_pool_size": settings.MONGODB_MAX_POOL_SIZE,
            "max_idle_time_ms": settings.MONGODB_MAX_IDLE_TIME_MS,
        }

        uptime_seconds = int(time.time() - self._start_time)

        return {
            "uptime_seconds": uptime_seconds,
            "system_resources": {
                "process_cpu_percent": cpu_pct,
                "process_memory_rss_mb": memory_mb,
                "process_memory_percent": memory_pct,
                "thread_count": thread_count,
            },
            "http_traffic": {
                "total_requests": total_reqs,
                "status_2xx": self._http_errors_2xx,
                "status_4xx": err_4xx,
                "status_5xx": err_5xx,
                "error_rate_percent": error_rate_pct,
                "status_code_distribution": status_dist,
            },
            "latencies_ms": {
                "api_request": api_lat,
                "mongodb_query": mongo_lat,
                "gemini_api": gemini_lat,
                "gnani_tts": gnani_lat,
            },
            "cache_telemetry": cache_stats,
            "connection_pools": pool_stats,
        }

    def generate_prometheus_metrics(self) -> str:
        """Format metrics into standard Prometheus exposition format."""
        data = self.get_system_metrics()
        lines: List[str] = [
            "# HELP samaan_uptime_seconds Process uptime in seconds",
            "# TYPE samaan_uptime_seconds gauge",
            f"samaan_uptime_seconds {data['uptime_seconds']}",
            "",
            "# HELP samaan_process_cpu_percent Current process CPU utilization percentage",
            "# TYPE samaan_process_cpu_percent gauge",
            f"samaan_process_cpu_percent {data['system_resources']['process_cpu_percent']}",
            "",
            "# HELP samaan_process_memory_rss_mb Resident memory usage in megabytes",
            "# TYPE samaan_process_memory_rss_mb gauge",
            f"samaan_process_memory_rss_mb {data['system_resources']['process_memory_rss_mb']}",
            "",
            "# HELP samaan_http_requests_total Total HTTP requests handled",
            "# TYPE samaan_http_requests_total counter",
            f"samaan_http_requests_total {data['http_traffic']['total_requests']}",
            "",
            "# HELP samaan_http_error_rate_percent HTTP 4xx/5xx error rate percentage",
            "# TYPE samaan_http_error_rate_percent gauge",
            f"samaan_http_error_rate_percent {data['http_traffic']['error_rate_percent']}",
            "",
            "# HELP samaan_api_latency_p95_ms P95 API request latency in milliseconds",
            "# TYPE samaan_api_latency_p95_ms gauge",
            f"samaan_api_latency_p95_ms {data['latencies_ms']['api_request']['p95']}",
            "",
            "# HELP samaan_api_latency_p50_ms P50 API request latency in milliseconds",
            "# TYPE samaan_api_latency_p50_ms gauge",
            f"samaan_api_latency_p50_ms {data['latencies_ms']['api_request']['p50']}",
            "",
            "# HELP samaan_mongo_latency_p95_ms P95 MongoDB query latency in milliseconds",
            "# TYPE samaan_mongo_latency_p95_ms gauge",
            f"samaan_mongo_latency_p95_ms {data['latencies_ms']['mongodb_query']['p95']}",
            "",
            "# HELP samaan_cache_hit_ratio_percent Custom cache hit ratio percentage",
            "# TYPE samaan_cache_hit_ratio_percent gauge",
            f"samaan_cache_hit_ratio_percent {data['cache_telemetry']['hit_ratio_percent']}",
            "",
            "# HELP samaan_cache_memory_bytes L1 cache memory footprint in bytes",
            "# TYPE samaan_cache_memory_bytes gauge",
            f"samaan_cache_memory_bytes {data['cache_telemetry']['l1_bytes']}",
        ]

        # Status code breakdowns
        for sc, cnt in data["http_traffic"]["status_code_distribution"].items():
            lines.append(f'samaan_http_responses_total{{code="{sc}"}} {cnt}')

        return "\n".join(lines) + "\n"


# Global singleton monitoring instance
system_metrics = SystemMetricsCollector()

