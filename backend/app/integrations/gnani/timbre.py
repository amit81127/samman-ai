"""
Gnani Timbre TTS Adapter
========================
Implements the SpeechSynthesizer protocol using Gnani AI Timbre v3.0 API.
Provides high-fidelity multilingual voice synthesis with local safety fallback.
"""

import base64
import logging
import os
import tempfile
from typing import Protocol

import httpx

from app.core.config import settings
from app.core.cache import cache
from app.integrations.gnani.client import get_gnani_tts_client

logger = logging.getLogger(__name__)

SUPPORTED_GNANI_VOICES = {
    "avinash", "shivani", "lakshmi", "kalpana", "shubham",
    "prakash", "devansh", "yashraj", "chetana", "vasudha",
    "harshad", "riyaa", "tarika",
}

VOICE_MAP = {
    "female": "Shivani",
    "female_1": "Shivani",
    "female_2": "Lakshmi",
    "female_3": "Kalpana",
    "male": "Prakash",
    "male_1": "Prakash",
    "male_2": "Avinash",
    "male_3": "Shubham",
}

LANGUAGE_MAP = {
    "en": "en-IN",
    "en-us": "en-IN",
    "en-in": "en-IN",
    "hi": "hi-IN",
    "hi-in": "hi-IN",
    "kn": "kn-IN",
    "kn-in": "kn-IN",
    "ta": "ta-IN",
    "ta-in": "ta-IN",
    "te": "te-IN",
    "te-in": "te-IN",
    "mr": "mr-IN",
    "mr-in": "mr-IN",
    "bn": "bn-IN",
    "bn-in": "bn-IN",
    "gu": "gu-IN",
    "gu-in": "gu-IN",
    "ml": "ml-IN",
    "ml-in": "ml-IN",
    "pa": "pa-IN",
    "pa-in": "pa-IN",
}


def _resolve_voice(voice: str | None) -> str:
    """Normalize and map voice identifiers to supported Gnani Timbre voices."""
    if not voice:
        return getattr(settings, "GNANI_DEFAULT_VOICE", "Shivani")
    v_lower = voice.strip().lower()
    if v_lower in SUPPORTED_GNANI_VOICES:
        return v_lower.capitalize()
    return VOICE_MAP.get(v_lower, getattr(settings, "GNANI_DEFAULT_VOICE", "Shivani"))


def _resolve_language(language: str | None) -> str:
    """Normalize and map language codes to Gnani supported BCP-47 codes."""
    if not language:
        return getattr(settings, "GNANI_DEFAULT_LANGUAGE", "en-IN")
    l_lower = language.strip().lower()
    return LANGUAGE_MAP.get(l_lower, getattr(settings, "GNANI_DEFAULT_LANGUAGE", "en-IN"))


def _synthesize_local_fallback(text: str) -> bytes:
    """Local pyttsx3 fallback in case Gnani service is temporarily unreachable."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        fd, temp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            with open(temp_path, "rb") as f:
                data = f.read()
            if data and len(data) > 44:  # Valid non-empty WAV
                logger.info("Generated fallback speech audio via local engine (%d bytes)", len(data))
                return data
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as exc:
        logger.error("Local speech fallback failed: %s", exc)
    raise RuntimeError("Speech synthesis failed on both Gnani AI and local fallback")


class SpeechSynthesizer(Protocol):
    """Interface that all TTS adapters must implement."""
    async def synthesize(
        self,
        text: str,
        language: str,
        voice: str | None = None,
        api_key: str | None = None,
    ) -> bytes:
        ...


class GnaniTimbreAdapter:
    """
    Calls Gnani AI Timbre v3.0 to convert approved text to high-fidelity audio bytes.

    This adapter is the ONLY place that sends text to Gnani.
    It never receives arbitrary text — only text loaded from an
    approved message record by the SpeechService.
    Supports user-specific personal Gnani API keys as well as system keys.
    """

    async def synthesize(
        self,
        text: str,
        language: str,
        voice: str | None = None,
        api_key: str | None = None,
    ) -> bytes:
        """
        Synthesize speech from approved text using Gnani AI Timbre.

        Args:
            text: The exact approved text to synthesize.
            language: Language code e.g. "en-IN", "hi-IN", "kn-IN", "ta-IN"
            voice: Voice ID from Gnani's supported voice list (e.g. "Shivani", "Prakash", "Avinash")
            api_key: Optional personal Gnani AI API key for this person/user.

        Returns:
            Raw WAV audio bytes.
        """
        resolved_voice = _resolve_voice(voice)
        resolved_lang = _resolve_language(language)
        model_name = getattr(settings, "GNANI_DEFAULT_MODEL", "timbre-v3.0")

        # 1. High-Speed Audio Cache Lookup (<1ms)
        cache_key = f"tts:{resolved_lang}:{resolved_voice}:{text.strip().lower()}"
        cached_audio = await cache.get_bytes(cache_key)
        if cached_audio:
            logger.info("Gnani TTS Audio Cache HIT for '%s' (0ms, %d bytes)", text[:30], len(cached_audio))
            return cached_audio

        request_body = {
            "text": text,
            "voice": resolved_voice,
            "model": model_name,
            "language": resolved_lang,
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 22050,
                "num_channels": 1,
                "sample_width": 2,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        }

        headers = None
        if api_key and api_key.strip():
            headers = {
                "X-API-Key-ID": api_key.strip(),
                "Content-Type": "application/json",
            }

        client = get_gnani_tts_client()
        try:
            response = await client.post("/inference", json=request_body, headers=headers)

            if response.status_code == 200:
                audio_bytes = None
                content_type = response.headers.get("content-type", "")
                if "audio" in content_type:
                    audio_bytes = response.content
                else:
                    data = response.json()
                    if "audio_data" in data:
                        audio_bytes = base64.b64decode(data["audio_data"])
                    elif isinstance(data, dict) and "data" in data and isinstance(data["data"], str):
                        audio_bytes = base64.b64decode(data["data"])
                    else:
                        logger.warning("Unexpected Gnani response JSON structure: %s", list(data.keys()) if isinstance(data, dict) else type(data))

                if audio_bytes:
                    # Cache audio bytes for 7 days
                    await cache.set_bytes(cache_key, audio_bytes, ttl=604800)
                    return audio_bytes
            else:
                logger.error(
                    "Gnani TTS returned error status %d: %s",
                    response.status_code,
                    response.text[:300],
                )

        except (httpx.TimeoutException, httpx.RequestError) as exc:
            logger.warning("Gnani Timbre API request error (%s): %s. Attempting fallback.", type(exc).__name__, exc)
        except Exception as exc:
            logger.warning("Unexpected Gnani TTS exception: %s. Attempting fallback.", exc)

        # Fallback to local audio engine so users are never blocked from speech
        return _synthesize_local_fallback(text)
