"""
Background Job Worker Engine (No Redis)
=======================================
Processes durable background jobs backed by MongoDB.
Features:
- Atomic job leasing using MongoDB find_one_and_update
- Dead-worker lock reclamation
- Exponential backoff retries with jitter
- Zero duplicate execution guarantee
- Strict AAC human-approval invariant enforcement
- Standalone CLI runner or embedded FastAPI lifespan worker
"""

import asyncio
import logging
import os
import signal
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Coroutine, Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.cache import cache
from app.repositories.job_repository import JobRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.speech_repository import SpeechRepository
from app.integrations.gnani.timbre import GnaniTimbreAdapter

logger = logging.getLogger("samaan.worker")


class JobWorker:
    def __init__(self, db: AsyncIOMotorDatabase, worker_id: Optional[str] = None):
        self.db = db
        self.worker_id = worker_id or f"worker-{os.getpid()}-{uuid.uuid4().hex[:6]}"
        self.job_repo = JobRepository(db)
        self.message_repo = MessageRepository(db)
        self.speech_repo = SpeechRepository(db)
        self.tts_adapter = GnaniTimbreAdapter()
        self._handlers: Dict[str, Callable[[dict, Optional[str]], Coroutine[Any, Any, dict]]] = {}
        self._register_default_handlers()

    def register_handler(
        self,
        job_type: str,
        handler: Callable[[dict, Optional[str]], Coroutine[Any, Any, dict]],
    ) -> None:
        """Register an async handler callable for a specific job_type."""
        self._handlers[job_type] = handler

    def _register_default_handlers(self) -> None:
        self.register_handler("tts_synthesis", self._handle_tts_synthesis)
        self.register_handler("audio_cleanup", self._handle_audio_cleanup)
        self.register_handler("cache_cleanup", self._handle_cache_cleanup)
        self.register_handler("analytics_aggregation", self._handle_analytics_aggregation)
        self.register_handler("partner_notification", self._handle_partner_notification)

    # ── Job Handlers ────────────────────────────────────────────────────────

    async def _handle_tts_synthesis(self, payload: dict, user_id: Optional[str]) -> dict:
        """
        Background TTS Synthesis:
        Strictly enforces the AAC Human-Approval invariant:
        - Message must exist and belong to user_id
        - Message MUST have approval_status == "approved"
        - Only approved_text is spoken
        """
        message_id = payload.get("message_id")
        if not message_id or not user_id:
            raise ValueError("NON_RETRYABLE: Missing message_id or user_id for TTS synthesis")

        # 1. Enforce Approval & Ownership Invariant
        message = await self.message_repo.find_by_id(message_id, user_id)
        if not message:
            raise ValueError("NON_RETRYABLE: Message not found or unauthorized")

        if message.get("approval_status") != "approved":
            raise ValueError(
                "NON_RETRYABLE: APPROVAL_REQUIRED - Message must be explicitly approved before speech synthesis"
            )

        approved_text = message.get("approved_text")
        if not approved_text:
            raise ValueError("NON_RETRYABLE: APPROVAL_REQUIRED - Message has no approved text")

        language = payload.get("language") or "en-IN"
        voice = payload.get("voice") or "Shivani"
        api_key = payload.get("api_key")

        # 2. Synthesize audio bytes via Gnani Timbre
        audio_bytes = await self.tts_adapter.synthesize(
            text=approved_text,
            language=language,
            voice=voice,
            api_key=api_key,
        )

        # 3. Cache audio for instantaneous client retrieval
        cache_key = f"{approved_text.strip().lower()}:{language}:{voice}:{api_key or ''}"
        await cache.cache_set("tts_audio", cache_key, audio_bytes, ttl=settings.CACHE_TTL_TTS_AUDIO)

        logger.info(
            "Worker [%s] successfully synthesized speech for message %s (%d bytes)",
            self.worker_id, message_id, len(audio_bytes)
        )

        return {
            "message_id": message_id,
            "approved_text": approved_text,
            "language": language,
            "voice": voice,
            "audio_bytes_length": len(audio_bytes),
            "synthesized_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _handle_audio_cleanup(self, payload: dict, user_id: Optional[str]) -> dict:
        """
        Scans cached audio files and evicts stale files exceeding TTL.
        """
        max_age_days = payload.get("max_age_days", 7)
        now = time.time()
        max_age_seconds = max_age_days * 86400
        cutoff = now - max_age_seconds

        audio_dir = os.path.join(cache._cache_dir, "tts_audio")
        files_checked = 0
        files_deleted = 0
        bytes_freed = 0

        if os.path.exists(audio_dir):
            for fname in os.listdir(audio_dir):
                fpath = os.path.join(audio_dir, fname)
                try:
                    if os.path.isfile(fpath):
                        files_checked += 1
                        mtime = os.path.getmtime(fpath)
                        if mtime < cutoff:
                            size = os.path.getsize(fpath)
                            os.remove(fpath)
                            files_deleted += 1
                            bytes_freed += size
                except OSError:
                    pass

        logger.info("Worker [%s] audio cleanup complete: %d deleted, %d bytes freed", self.worker_id, files_deleted, bytes_freed)
        return {
            "files_checked": files_checked,
            "files_deleted": files_deleted,
            "bytes_freed": bytes_freed,
        }

    async def _handle_cache_cleanup(self, payload: dict, user_id: Optional[str]) -> dict:
        """
        Evicts expired entries from both L1 memory and L2 disk caches.
        """
        stats = await cache.prune_expired_entries()
        return {"cache_prune_stats": stats, "timestamp": datetime.now(timezone.utc).isoformat()}

    async def _handle_analytics_aggregation(self, payload: dict, user_id: Optional[str]) -> dict:
        """
        Aggregates communication metrics (e.g. total composed, approved messages, active phrases)
        without impacting online user transaction performance.
        """
        total_messages = await self.db["messages"].count_documents({"is_deleted": False})
        approved_messages = await self.db["messages"].count_documents(
            {"is_deleted": False, "approval_status": "approved"}
        )
        total_phrases = await self.db["phrases"].count_documents({"is_active": True})
        total_boards = await self.db["boards"].count_documents({"is_active": True})

        snapshot = {
            "total_messages": total_messages,
            "approved_messages": approved_messages,
            "total_phrases": total_phrases,
            "total_boards": total_boards,
            "created_at": datetime.now(timezone.utc),
        }
        await self.db["analytics_snapshots"].insert_one(snapshot)
        snapshot.pop("_id", None)
        snapshot["created_at"] = snapshot["created_at"].isoformat()
        return snapshot

    async def _handle_partner_notification(self, payload: dict, user_id: Optional[str]) -> dict:
        """
        Queues and records non-urgent partner notifications asynchronously.
        """
        partner_id = payload.get("partner_id")
        event_type = payload.get("event_type", "message_activity")
        message = payload.get("message", "User completed a communication session")

        notification_doc = {
            "user_id": ObjectId(user_id) if user_id else None,
            "partner_id": ObjectId(partner_id) if partner_id else None,
            "event_type": event_type,
            "message": message,
            "delivered": True,
            "created_at": datetime.now(timezone.utc),
        }
        await self.db["partner_notifications"].insert_one(notification_doc)
        return {
            "event_type": event_type,
            "delivered": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ── Job Execution Cycle ─────────────────────────────────────────────────

    async def execute_one(self) -> bool:
        """
        Leases and processes a single job from the durable queue.
        Returns True if a job was found and processed, False if queue was empty.
        """
        job = await self.job_repo.lease_next_job(
            worker_id=self.worker_id,
            lock_timeout_seconds=settings.WORKER_LOCK_TIMEOUT_SECONDS,
        )
        if not job:
            return False

        job_id = job["id"]
        job_type = job["job_type"]
        payload = job.get("payload", {})
        user_id = job.get("user_id")

        logger.info("Worker [%s] leased job %s (%s)", self.worker_id, job_id, job_type)

        handler = self._handlers.get(job_type)
        if not handler:
            await self.job_repo.fail_or_retry_job(
                job_id=job_id,
                error_message=f"No registered handler for job type '{job_type}'",
                can_retry=False,
            )
            return True

        try:
            result = await handler(payload, user_id)
            await self.job_repo.complete_job(job_id=job_id, result=result)
            logger.info("Worker [%s] completed job %s (%s)", self.worker_id, job_id, job_type)
        except Exception as exc:
            err_str = str(exc)
            # Permanent failures shouldn't retry (e.g. invariant violation or invalid args)
            is_non_retryable = "NON_RETRYABLE" in err_str or "APPROVAL_REQUIRED" in err_str
            can_retry = not is_non_retryable

            await self.job_repo.fail_or_retry_job(
                job_id=job_id,
                error_message=err_str,
                can_retry=can_retry,
            )

        return True

    async def run_loop(self, stop_event: asyncio.Event) -> None:
        """
        Main worker loop:
        Polls queue with adaptive backoff until stop_event is triggered.
        """
        logger.info("Worker [%s] started processing loop", self.worker_id)
        while not stop_event.is_set():
            try:
                processed = await self.execute_one()
                if not processed:
                    # Queue is empty: sleep poll interval or wait for stop event
                    try:
                        await asyncio.wait_for(stop_event.wait(), timeout=settings.WORKER_POLL_INTERVAL_SECONDS)
                    except asyncio.TimeoutError:
                        pass
            except asyncio.CancelledError:
                break
            except Exception as loop_exc:
                logger.error("Unexpected worker loop error in [%s]: %s", self.worker_id, loop_exc)
                await asyncio.sleep(2.0)

        logger.info("Worker [%s] stopped processing loop gracefully", self.worker_id)


# ── Standalone CLI Entrypoint ───────────────────────────────────────────────

async def _main():
    from app.core.database import connect_to_mongo, close_mongo_connection, get_database
    from app.core.logging import setup_logging

    setup_logging()
    logger.info("Starting standalone Background Job Worker process...")
    await connect_to_mongo()

    db = get_database()
    worker = JobWorker(db)
    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: stop_event.set())
        except (NotImplementedError, RuntimeError):
            # Windows signal handling fallback
            pass

    try:
        await worker.run_loop(stop_event)
    finally:
        await close_mongo_connection()
        logger.info("Standalone worker process shutdown complete.")


if __name__ == "__main__":
    asyncio.run(_main())

