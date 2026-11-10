"""
Gemini LLM Prometheus Metrics & Telemetry
=========================================
Tracks request counts, latencies, tokens, fallback events, quota consumption,
and routing decisions with low-cardinality labels.
Exposes standard Prometheus scrape format via generate_prometheus_metrics().
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Tuple


class LLMMetricsCollector:
    """Thread-safe Prometheus metrics collector for Gemini infrastructure."""

    def __init__(self):
        self._lock = Lock()
        # Counters: (name, tuple(sorted(labels.items()))) -> value
        self._counters: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], float] = defaultdict(float)
        # Latency histograms / summaries: (name, tuple(sorted(labels.items()))) -> list of latencies
        self._latencies: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], List[float]] = defaultdict(list)
        # Gauges: (name, tuple(sorted(labels.items()))) -> value
        self._gauges: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], float] = defaultdict(float)

    def _labels_key(self, labels: Dict[str, str]) -> Tuple[Tuple[str, str], ...]:
        return tuple(sorted((k, str(v)) for k, v in labels.items()))

    def increment_requests(self, model: str, status: str):
        with self._lock:
            key = ("gemini_requests_total", self._labels_key({"model": model, "status": status}))
            self._counters[key] += 1.0

    def record_duration(self, model: str, duration_seconds: float):
        with self._lock:
            key = ("gemini_request_duration_seconds", self._labels_key({"model": model}))
            self._latencies[key].append(duration_seconds)
            # Keep rolling window to limit memory
            if len(self._latencies[key]) > 1000:
                self._latencies[key].pop(0)

    def record_tokens(self, model: str, token_type: str, count: int):
        if count <= 0:
            return
        with self._lock:
            key = ("gemini_tokens_total", self._labels_key({"model": model, "token_type": token_type}))
            self._counters[key] += float(count)

    def record_fallback(self, from_model: str, to_model: str, reason: str):
        with self._lock:
            key = ("gemini_fallback_total", self._labels_key({"from_model": from_model, "to_model": to_model, "reason": reason}))
            self._counters[key] += 1.0

    def record_error(self, model: str, error_type: str):
        with self._lock:
            key = ("gemini_errors_total", self._labels_key({"model": model, "error_type": error_type}))
            self._counters[key] += 1.0

    def record_routing_decision(self, model: str, reason: str):
        with self._lock:
            key = ("gemini_routing_decisions_total", self._labels_key({"model": model, "reason": reason}))
            self._counters[key] += 1.0

    def update_quota_remaining(self, model: str, window: str, remaining: float):
        with self._lock:
            key = ("gemini_quota_remaining", self._labels_key({"model": model, "window": window}))
            self._gauges[key] = float(remaining)

    def generate_prometheus_metrics(self) -> str:
        """Render all collected metrics in standard Prometheus exposition format."""
        lines = []
        with self._lock:
            # 1. Requests total
            lines.append("# HELP gemini_requests_total Total number of Gemini API requests")
            lines.append("# TYPE gemini_requests_total counter")
            for (name, label_pairs), val in sorted(self._counters.items()):
                if name == "gemini_requests_total":
                    labels_str = ",".join(f'{k}="{v}"' for k, v in label_pairs)
                    lines.append(f"{name}{{{labels_str}}} {val}")

            # 2. Duration / Latency (Count & Sum)
            lines.append("# HELP gemini_request_duration_seconds Gemini request latency in seconds")
            lines.append("# TYPE gemini_request_duration_seconds summary")
            for (name, label_pairs), durations in sorted(self._latencies.items()):
                if durations:
                    labels_str = ",".join(f'{k}="{v}"' for k, v in label_pairs)
                    total_sum = sum(durations)
                    count = len(durations)
                    lines.append(f"{name}_sum{{{labels_str}}} {total_sum:.4f}")
                    lines.append(f"{name}_count{{{labels_str}}} {count}")

            # 3. Tokens total
            lines.append("# HELP gemini_tokens_total Total tokens consumed by Gemini models")
            lines.append("# TYPE gemini_tokens_total counter")
            for (name, label_pairs), val in sorted(self._counters.items()):
                if name == "gemini_tokens_total":
                    labels_str = ",".join(f'{k}="{v}"' for k, v in label_pairs)
                    lines.append(f"{name}{{{labels_str}}} {val}")

            # 4. Fallback total
            lines.append("# HELP gemini_fallback_total Total model fallback transitions")
            lines.append("# TYPE gemini_fallback_total counter")
            for (name, label_pairs), val in sorted(self._counters.items()):
                if name == "gemini_fallback_total":
                    labels_str = ",".join(f'{k}="{v}"' for k, v in label_pairs)
                    lines.append(f"{name}{{{labels_str}}} {val}")

            # 5. Errors total
            lines.append("# HELP gemini_errors_total Total errors encountered per Gemini model")
            lines.append("# TYPE gemini_errors_total counter")
            for (name, label_pairs), val in sorted(self._counters.items()):
                if name == "gemini_errors_total":
                    labels_str = ",".join(f'{k}="{v}"' for k, v in label_pairs)
                    lines.append(f"{name}{{{labels_str}}} {val}")

            # 6. Routing decisions total
            lines.append("# HELP gemini_routing_decisions_total Decisions made by model router")
            lines.append("# TYPE gemini_routing_decisions_total counter")
            for (name, label_pairs), val in sorted(self._counters.items()):
                if name == "gemini_routing_decisions_total":
                    labels_str = ",".join(f'{k}="{v}"' for k, v in label_pairs)
                    lines.append(f"{name}{{{labels_str}}} {val}")

            # 7. Quota remaining gauges
            lines.append("# HELP gemini_quota_remaining Estimated remaining safety quota")
            lines.append("# TYPE gemini_quota_remaining gauge")
            for (name, label_pairs), val in sorted(self._gauges.items()):
                if name == "gemini_quota_remaining":
                    labels_str = ",".join(f'{k}="{v}"' for k, v in label_pairs)
                    lines.append(f"{name}{{{labels_str}}} {val}")

        return "\n".join(lines) + "\n"


# Global metrics collector instance
llm_metrics = LLMMetricsCollector()
