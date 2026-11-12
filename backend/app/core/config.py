"""
Application Configuration
=========================
All settings loaded from environment variables via pydantic-settings.
Add any new env var here as a typed field.
"""

import json
from pathlib import Path
from typing import List, Optional, Union
from pydantic import field_validator
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
    PORT: Optional[int] = None
    APP_DEBUG: bool = True

    # ── MongoDB ───────────────────────────────────────────────────────────
    MONGODB_URI: str
    DATABASE_NAME: str = "samaan_ai"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_MAX_IDLE_TIME_MS: int = 45000
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 5000
    MONGODB_CONNECT_TIMEOUT_MS: int = 5000
    MONGODB_SOCKET_TIMEOUT_MS: int = 10000
    MONGODB_WAIT_QUEUE_TIMEOUT_MS: int = 5000

    # ── Cache Configuration (L1 In-Memory + L2 Local Disk) ───────────────
    CACHE_DIR_PATH: Optional[str] = None
    CACHE_MAX_MEMORY_BYTES: int = 64 * 1024 * 1024  # 64 MB
    CACHE_MAX_MEMORY_ENTRIES: int = 5000
    CACHE_MAX_DISK_BYTES: int = 256 * 1024 * 1024   # 256 MB
    CACHE_TTL_USER_PROFILES: int = 300              # 5 minutes
    CACHE_TTL_BOARDS: int = 300                     # 5 minutes
    CACHE_TTL_PHRASES: int = 300                    # 5 minutes
    CACHE_TTL_AI_CANDIDATES: int = 3600             # 1 hour
    CACHE_TTL_TTS_METADATA: int = 3600              # 1 hour
    CACHE_TTL_TTS_AUDIO: int = 604800               # 7 days
    CACHE_TTL_APP_DATA: int = 300                   # 5 minutes

    # ── Security / JWT ────────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── CORS ──────────────────────────────────────────────────────────────
    FRONTEND_URL: Optional[str] = "https://samman-ai.vercel.app"
    ALLOWED_ORIGINS: List[str] = [
        "https://samman-ai.vercel.app",
        "https://samaan-ai.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        base_origins = [
            "https://samman-ai.vercel.app",
            "https://samaan-ai.vercel.app",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
        parsed_origins: List[str] = []
        if isinstance(v, str):
            stripped = v.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, list):
                        parsed_origins = [str(item).strip().rstrip("/") for item in parsed if item]
                except Exception:
                    pass
            if not parsed_origins:
                parsed_origins = [origin.strip().rstrip("/") for origin in stripped.split(",") if origin.strip()]
        elif isinstance(v, list):
            parsed_origins = [str(item).strip().rstrip("/") for item in v if item]

        combined = list(base_origins)
        for o in parsed_origins:
            if o and o not in combined:
                combined.append(o)
        return combined

    @property
    def all_allowed_origins(self) -> List[str]:
        origins = list(self.ALLOWED_ORIGINS)
        if self.FRONTEND_URL:
            clean = self.FRONTEND_URL.strip().rstrip("/")
            if clean and clean not in origins:
                origins.append(clean)
        return origins

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

    # ── Background Worker Configuration (No Redis) ────────────────────────
    WORKER_ENABLED: bool = True
    WORKER_POLL_INTERVAL_SECONDS: float = 2.0
    WORKER_LOCK_TIMEOUT_SECONDS: int = 120
    WORKER_MAX_RETRIES: int = 3
    WORKER_CONCURRENCY: int = 3

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
