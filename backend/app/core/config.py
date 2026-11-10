"""
Application Configuration
=========================
All settings loaded from environment variables via pydantic-settings.
Add any new env var here as a typed field.
"""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_file = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_env_file) if _env_file.exists() else ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True

    # ── MongoDB ───────────────────────────────────────────────────────────
    MONGODB_URI: str
    DATABASE_NAME: str = "samaan_ai"

    # ── Security / JWT ────────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── CORS ──────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # ── Gemini AI & Intelligent Routing ───────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_PRIMARY_MODEL: str = "gemini-3.5-flash-lite"
    GEMINI_ADVANCED_MODEL: str = "gemini-3.8-flash"
    GEMINI_FALLBACK_MODEL: str = "gemini-flash-lite-latest"
    GEMINI_FALLBACK_MODELS: str = "gemini-flash-lite-latest,gemini-3.5-flash,gemini-3.6-flash,gemini-3.1-flash-lite,gemini-3.8-flash"
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"

    GEMINI_ENABLE_SMART_ROUTING: bool = True
    GEMINI_ENABLE_FALLBACK: bool = True

    GEMINI_LITE_DAILY_LIMIT: int = 450
    GEMINI_ADVANCED_DAILY_LIMIT: int = 18
    GEMINI_LITE_RPM_LIMIT: int = 12
    GEMINI_ADVANCED_RPM_LIMIT: int = 4

    GEMINI_TEMPERATURE: float = 0.2
    GEMINI_MAX_OUTPUT_TOKENS: int = 180
    GEMINI_TIMEOUT_SECONDS: int = 15
    GEMINI_MAX_RETRIES: int = 3
    GEMINI_BACKOFF_BASE_SECONDS: float = 2.0
    GEMINI_BACKOFF_MAX_SECONDS: float = 15.0
    GEMINI_CIRCUIT_BREAKER_ENABLED: bool = True
    GEMINI_CIRCUIT_BREAKER_COOLDOWN: int = 30
    GEMINI_CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 3
    GEMINI_QUOTA_TIMEZONE: str = "Asia/Kolkata"

    REDIS_URL: str = ""

    # ── Gnani AI Timbre TTS ───────────────────────────────────────────────
    GNANI_API_KEY: str = ""
    GNANI_TTS_BASE_URL: str = "https://api.vachana.ai/api/v1/tts"
    GNANI_STT_BASE_URL: str = "https://api.vachana.ai/api/v1/stt"
    GNANI_TIMEOUT_SECONDS: int = 15
    GNANI_DEFAULT_LANGUAGE: str = "en-IN"
    GNANI_DEFAULT_VOICE: str = "Shivani"
    GNANI_DEFAULT_MODEL: str = "timbre-v3.0"

    # ── Rate Limiting ─────────────────────────────────────────────────────
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_AI_GENERATION: str = "10/minute"
    RATE_LIMIT_TTS: str = "20/minute"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


settings = Settings()
