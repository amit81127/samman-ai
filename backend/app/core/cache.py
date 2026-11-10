"""
SAMAAN AI — High-Performance Multi-Tier Caching System
======================================================
Provides sub-millisecond in-memory LRU/TTL caching with persistent disk storage
for AI model responses, speech synthesis audio, and user preferences.
"""

import asyncio
from collections import OrderedDict
import hashlib
import json
import logging
import os
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Cache directory for persistent audio and model responses
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".cache")
TTS_CACHE_DIR = os.path.join(CACHE_DIR, "tts")


class CacheEntry:
    __slots__ = ("value", "expires_at", "is_bytes")

    def __init__(self, value: Any, expires_at: float, is_bytes: bool = False):
        self.value = value
        self.expires_at = expires_at
        self.is_bytes = is_bytes

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class CacheManager:
    """
    Thread-safe, non-blocking in-memory LRU cache with TTL support and
    persistent disk-backed binary storage for TTS audio.
    """

    def __init__(self, max_memory_entries: int = 2000):
        self._memory: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_entries = max_memory_entries
        self._lock = asyncio.Lock()
        self._ensure_disk_cache_dir()

    def _ensure_disk_cache_dir(self) -> None:
        try:
            os.makedirs(TTS_CACHE_DIR, exist_ok=True)
        except Exception as exc:
            logger.warning("Failed to create disk cache directory %s: %s", TTS_CACHE_DIR, exc)

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve an item from memory cache."""
        async with self._lock:
            entry = self._memory.get(key)
            if not entry:
                return None

            if entry.is_expired():
                del self._memory[key]
                return None

            # Move to end (MRU)
            self._memory.move_to_end(key)
            return entry.value

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Store an item in memory cache with TTL (seconds)."""
        async with self._lock:
            expires_at = time.time() + ttl

            # Evict oldest if capacity reached
            if len(self._memory) >= self._max_entries and key not in self._memory:
                self._memory.popitem(last=False)

            self._memory[key] = CacheEntry(value=value, expires_at=expires_at, is_bytes=False)
            self._memory.move_to_end(key)

    async def get_bytes(self, key: str) -> Optional[bytes]:
        """
        Retrieve binary data (e.g. audio/wav) from memory cache or persistent disk cache.
        Returns bytes or None.
        """
        # 1. Check in-memory cache first (sub-millisecond <1ms)
        async with self._lock:
            entry = self._memory.get(key)
            if entry and not entry.is_expired():
                self._memory.move_to_end(key)
                return entry.value

        # 2. Check disk cache if not in memory (1-2ms)
        disk_path = os.path.join(TTS_CACHE_DIR, f"{self._hash_key(key)}.wav")
        if os.path.exists(disk_path):
            try:
                # Read asynchronously without blocking event loop
                loop = asyncio.get_running_loop()
                data = await loop.run_in_executor(None, self._read_file_sync, disk_path)
                if data and len(data) > 44:  # Non-empty valid WAV
                    # Re-populate into memory cache for next instant hit
                    await self.set_bytes(key, data, ttl=604800)  # 7 days
                    return data
            except Exception as exc:
                logger.warning("Error reading disk cache %s: %s", disk_path, exc)

        return None

    async def set_bytes(self, key: str, data: bytes, ttl: int = 604800) -> None:
        """Store binary data in memory cache and persist to disk asynchronously."""
        if not data:
            return

        # 1. Store in memory cache
        async with self._lock:
            expires_at = time.time() + ttl
            if len(self._memory) >= self._max_entries and key not in self._memory:
                self._memory.popitem(last=False)

            self._memory[key] = CacheEntry(value=data, expires_at=expires_at, is_bytes=True)
            self._memory.move_to_end(key)

        # 2. Persist to disk asynchronously in executor
        disk_path = os.path.join(TTS_CACHE_DIR, f"{self._hash_key(key)}.wav")
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, self._write_file_sync, disk_path, data)
        except Exception as exc:
            logger.warning("Failed to write to disk cache %s: %s", disk_path, exc)

    @staticmethod
    def _read_file_sync(path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    @staticmethod
    def _write_file_sync(path: str, data: bytes) -> None:
        with open(path, "wb") as f:
            f.write(data)

    async def delete(self, key: str) -> None:
        """Evict a specific key from memory and disk."""
        async with self._lock:
            self._memory.pop(key, None)

        disk_path = os.path.join(TTS_CACHE_DIR, f"{self._hash_key(key)}.wav")
        if os.path.exists(disk_path):
            try:
                os.remove(disk_path)
            except Exception:
                pass

    async def clear(self) -> None:
        """Clear memory cache."""
        async with self._lock:
            self._memory.clear()


# Global singleton cache instance
cache = CacheManager()

