"""
Gnani HTTP Client
=================
Shared HTTPX async client for all Gnani API calls.
Handles authentication headers, persistent connection pooling, and base URL configuration.
"""

from typing import Optional
import httpx
from app.core.config import settings

_tts_client: Optional[httpx.AsyncClient] = None
_stt_client: Optional[httpx.AsyncClient] = None


def get_gnani_tts_client() -> httpx.AsyncClient:
    """Return a pooled HTTPX client pre-configured for Gnani Timbre TTS."""
    global _tts_client
    if _tts_client is None or _tts_client.is_closed:
        _tts_client = httpx.AsyncClient(
            base_url=settings.GNANI_TTS_BASE_URL or "https://api.vachana.ai/api/v1/tts",
            headers={
                "X-API-Key-ID": settings.GNANI_API_KEY,
                "Content-Type": "application/json",
            },
            timeout=float(settings.GNANI_TIMEOUT_SECONDS),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        )
    return _tts_client


def get_gnani_stt_client() -> httpx.AsyncClient:
    """Return a pooled HTTPX client pre-configured for Gnani Prisma STT."""
    global _stt_client
    if _stt_client is None or _stt_client.is_closed:
        _stt_client = httpx.AsyncClient(
            base_url=settings.GNANI_STT_BASE_URL or "https://api.vachana.ai/api/v1/stt",
            headers={
                "X-API-Key-ID": settings.GNANI_API_KEY,
                "Content-Type": "application/json",
            },
            timeout=float(settings.GNANI_TIMEOUT_SECONDS),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        )
    return _stt_client


async def close_gnani_clients() -> None:
    """Gracefully close HTTPX pooled clients upon application shutdown."""
    global _tts_client, _stt_client
    if _tts_client and not _tts_client.is_closed:
        await _tts_client.aclose()
        _tts_client = None
    if _stt_client and not _stt_client.is_closed:
        await _stt_client.aclose()
        _stt_client = None
