"""
SAMAAN AI — HTTP Performance, Timing & Compression Middleware
=============================================================
1. GZipMiddleware / SelectiveGZipMiddleware:
   - Compresses eligible JSON, text, and API responses (>= 500 bytes, level 6).
   - Skips media marked with Content-Encoding: identity (audio/wav, audio/mpeg,
     images, videos, pre-compressed archives, PDFs, event streams).
2. HTTPPerformanceMiddleware:
   - Injects Server-Timing (total;dur=X.XX) and X-Process-Time headers.
   - Sets adaptive, secure HTTP Cache-Control headers (private for user data,
     private-cached for synthesized audio, no-cache for health/metrics).
   - Ensures media and already-compressed payloads carry Content-Encoding: identity
     so standard GZipMiddleware bypasses them safely.
   - Emits structured, high-resolution request logs with zero credential leakage.
"""

import logging
import time
from typing import Tuple

from starlette.datastructures import Headers, MutableHeaders
from starlette.middleware.gzip import GZipMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("samaan.http")

# Content types that should NOT be compressed with GZip because they are already compressed
EXCLUDED_CONTENT_PREFIXES: Tuple[str, ...] = (
    "text/event-stream",
    "audio/",
    "image/",
    "video/",
    "application/zip",
    "application/x-zip-compressed",
    "application/gzip",
    "application/pdf",
    "application/octet-stream",
)


class SelectiveGZipMiddleware(GZipMiddleware):
    """
    Standard Starlette GZipMiddleware configured with SAMAAN AI production defaults.
    Uses Starlette's public, production-tested GZip implementation.
    """

    def __init__(self, app: ASGIApp, minimum_size: int = 500, compresslevel: int = 6) -> None:
        super().__init__(app, minimum_size=minimum_size, compresslevel=compresslevel)


class HTTPPerformanceMiddleware:
    """
    ASGI middleware providing:
    - Server-Timing: total;dur=X.XX
    - X-Process-Time: X.XXms
    - Safe bypass tagging for already-compressed / audio payloads (Content-Encoding: identity)
    - Cache-Control header management
    - High-resolution structured request logging and metrics recording
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        status_code = 200
        path = scope.get("path", "")
        method = scope.get("method", "")

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
                dur_ms = (time.perf_counter() - start_time) * 1000.0

                headers = MutableHeaders(scope=message)
                headers["Server-Timing"] = f"total;dur={dur_ms:.2f}"
                headers["X-Process-Time"] = f"{dur_ms:.2f}ms"

                content_type = headers.get("content-type", "").lower()

                # Protect already compressed / raw binary media from redundant GZip compression
                if any(content_type.startswith(prefix) for prefix in EXCLUDED_CONTENT_PREFIXES):
                    if "content-encoding" not in headers:
                        headers["Content-Encoding"] = "identity"

                # Apply adaptive cache control headers if not explicitly set by the handler
                if "cache-control" not in headers:
                    if content_type.startswith("audio/"):
                        headers["Cache-Control"] = "private, max-age=86400"
                    elif path.startswith(("/health", "/metrics")):
                        headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                    elif path.startswith("/api/v1/"):
                        headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
                    elif path == "/":
                        headers["Cache-Control"] = "public, max-age=3600"

            elif message["type"] == "http.response.body":
                if not message.get("more_body", False):
                    total_dur_ms = (time.perf_counter() - start_time) * 1000.0
                    try:
                        from app.core.monitoring import system_metrics
                        system_metrics.record_api_request(method, path, status_code, total_dur_ms)
                    except Exception:
                        pass

                    logger.info(
                        "HTTP %s %s -> %d (%.2fms)",
                        method,
                        path,
                        status_code,
                        total_dur_ms,
                    )

            await send(message)

        await self.app(scope, receive, send_wrapper)
