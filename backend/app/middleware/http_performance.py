"""
SAMAAN AI — HTTP Performance, Timing & Selective Compression Middleware
======================================================================
1. SelectiveGZipMiddleware:
   - Compresses eligible JSON, text, and API responses (>= 500 bytes, level 5).
   - Strictly skips already-compressed media (audio/wav, audio/mpeg, images, videos,
     pre-compressed archives, PDFs, event streams).
2. HTTPPerformanceMiddleware:
   - Injects Server-Timing (total;dur=X.XX) and X-Process-Time headers.
   - Sets adaptive, secure HTTP Cache-Control headers (private for user data,
     private-cached for synthesized audio, no-cache for health/metrics).
   - Emits structured, high-resolution request logs with zero credential leakage.
"""

import gzip
import io
import logging
import time
from typing import Tuple

from starlette.datastructures import Headers, MutableHeaders
from starlette.middleware.gzip import IdentityResponder
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


class SelectiveGZipResponder(IdentityResponder):
    """
    Custom GZip responder that selectively compresses responses based on content type,
    ensuring audio/wav and other media are never recompressed.
    """

    content_encoding = "gzip"

    def __init__(self, app: ASGIApp, minimum_size: int = 500, compresslevel: int = 5) -> None:
        super().__init__(app, minimum_size)
        self.compresslevel = compresslevel
        self.gzip_buffer = io.BytesIO()
        self.gzip_file = gzip.GzipFile(
            mode="wb",
            fileobj=self.gzip_buffer,
            compresslevel=compresslevel,
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        with self.gzip_buffer, self.gzip_file:
            await super().__call__(scope, receive, send)

    async def send_with_compression(self, message: Message) -> None:
        message_type = message["type"]

        if message_type == "http.response.start":
            self.initial_message = message
            headers = Headers(raw=self.initial_message["headers"])
            self.content_encoding_set = "content-encoding" in headers
            content_type = headers.get("content-type", "").lower()
            self.content_type_is_excluded = any(
                content_type.startswith(prefix) for prefix in EXCLUDED_CONTENT_PREFIXES
            )

        elif message_type == "http.response.body" and (self.content_encoding_set or self.content_type_is_excluded):
            if not self.started:
                self.started = True
                await self.send(self.initial_message)
            await self.send(message)

        elif message_type == "http.response.body" and not self.started:
            self.started = True
            body = message.get("body", b"")
            more_body = message.get("more_body", False)

            if len(body) < self.minimum_size and not more_body:
                # Payload is smaller than compression threshold; send uncompressed
                await self.send(self.initial_message)
                await self.send(message)
            elif not more_body:
                # Standard one-shot response
                body = self.apply_compression(body, more_body=False)
                headers = MutableHeaders(raw=self.initial_message["headers"])
                headers.add_vary_header("Accept-Encoding")
                if body != message["body"]:
                    headers["Content-Encoding"] = self.content_encoding
                    headers["Content-Length"] = str(len(body))
                    message["body"] = body

                await self.send(self.initial_message)
                await self.send(message)
            else:
                # Streaming response initial chunk
                body = self.apply_compression(body, more_body=True)
                headers = MutableHeaders(raw=self.initial_message["headers"])
                headers.add_vary_header("Accept-Encoding")
                if body != message["body"]:
                    headers["Content-Encoding"] = self.content_encoding
                    del headers["Content-Length"]
                    message["body"] = body

                await self.send(self.initial_message)
                await self.send(message)

        elif message_type == "http.response.body":
            # Streaming response subsequent chunks
            body = message.get("body", b"")
            more_body = message.get("more_body", False)
            message["body"] = self.apply_compression(body, more_body=more_body)
            await self.send(message)

        elif message_type == "http.response.pathsend":
            await self.send(self.initial_message)
            await self.send(message)

    def apply_compression(self, body: bytes, *, more_body: bool) -> bytes:
        self.gzip_file.write(body)
        if not more_body:
            self.gzip_file.close()

        compressed_data = self.gzip_buffer.getvalue()
        self.gzip_buffer.seek(0)
        self.gzip_buffer.truncate()
        return compressed_data


class SelectiveGZipMiddleware:
    """
    Middleware applying gzip compression to responses >= minimum_size bytes
    while excluding pre-compressed content types (audio, images, video, pdf, zip).
    """

    def __init__(self, app: ASGIApp, minimum_size: int = 500, compresslevel: int = 5) -> None:
        self.app = app
        self.minimum_size = minimum_size
        self.compresslevel = compresslevel

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        if "gzip" in headers.get("Accept-Encoding", ""):
            responder = SelectiveGZipResponder(
                self.app,
                minimum_size=self.minimum_size,
                compresslevel=self.compresslevel,
            )
        else:
            responder = IdentityResponder(self.app, minimum_size=self.minimum_size)

        await responder(scope, receive, send)


class HTTPPerformanceMiddleware:
    """
    ASGI middleware providing:
    - Server-Timing: total;dur=X.XX
    - X-Process-Time: X.XXms
    - Cache-Control header management
    - High-resolution structured request logging
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

                # Apply cache control headers if not explicitly set by the handler
                if "cache-control" not in headers:
                    content_type = headers.get("content-type", "").lower()
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

