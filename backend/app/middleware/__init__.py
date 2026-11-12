"""
SAMAAN AI — Middleware Package
==============================
Contains ASGI middlewares for HTTP performance, timing, compression,
and security logging.
"""

from starlette.middleware.gzip import GZipMiddleware
from app.middleware.http_performance import (
    HTTPPerformanceMiddleware,
    SelectiveGZipMiddleware,
)

__all__ = ["HTTPPerformanceMiddleware", "SelectiveGZipMiddleware", "GZipMiddleware"]
