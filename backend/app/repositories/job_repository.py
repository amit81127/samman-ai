"""
Background Job Repository
=========================
MongoDB data access for background_jobs collection.
Provides durable queue semantics without Redis:
- Atomic job leasing using find_one_and_update
- Dead-worker lock reclamation
- Exponential backoff retry scheduling
- Idempotency key deduplication
- User-scoped job isolation
"""

import logging
import random
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _serialize(doc: Optional[dict]) -> Optional[dict]:
    if doc is None:
        return None
    result = dict(doc)
    result["id"] = str(result.pop("_id"))
    for field in ("user_id",):
        if field in result and isinstance(result[field], ObjectId):
            result[field] = str(result[field])
    for key in ("created_at", "started_at", "completed_at", "scheduled_at", "locked_at"):
        if key in result and isinstance(result[key], datetime):
            result[key] = result[key].isoformat()
    return result


class JobRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["background_jobs"]

    async def create_job(
        self,
        job_type: str,
        payload: Dict[str, Any],
        user_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        max_retries: int = 3,
        scheduled_at: Optional[datetime] = None,
    ) -> dict:
        """
        Enqueue a new durable background job.
        If idempotency_key is provided and an active/completed job exists,
        returns the existing job to prevent duplicate execution.
        """
        now = _utcnow()
        scheduled_time = scheduled_at or now

        # Deduplication check via idempotency_key
        if idempotency_key:
            existing = await self._col.find_one({"idempotency_key": idempotency_key})
            if existing:
                # If existing job is pending, running, or completed, return it
                if existing.get("status") in ("pending", "running", "completed"):
                    logger.info("Found existing job for idempotency key %s (status: %s)", idempotency_key, existing.get("status"))
                    return _serialize(existing)
                # If previously failed/cancelled, we allow re-creating or retrying
                await self._col.delete_one({"_id": existing["_id"]})

        doc = {
            "job_type": job_type,
            "payload": payload,
            "status": "pending",
            "user_id": ObjectId(user_id) if user_id else None,
            "attempts": 0,
            "max_retries": max_retries,
            "scheduled_at": scheduled_time,
            "locked_at": None,
            "locked_by": None,
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error_message": None,
            "created_at": now,
        }
        if idempotency_key:
            doc["idempotency_key"] = idempotency_key

        try:
            result = await self._col.insert_one(doc)
            doc["_id"] = result.inserted_id
            return _serialize(doc)
        except DuplicateKeyError:
            if idempotency_key:
                existing = await self._col.find_one({"idempotency_key": idempotency_key})
                if existing:
                    return _serialize(existing)
            raise

    async def lease_next_job(
        self,
        worker_id: str,
        lock_timeout_seconds: int = 120,
    ) -> Optional[dict]:
        """
        Atomically lease the next available pending job or reclaim an expired lock.
        Guarantees zero duplicate job execution between concurrent workers.
        """
        now = _utcnow()
        stale_threshold = now - timedelta(seconds=lock_timeout_seconds)

        # Match jobs ready to run (including a 1-second margin for millisecond clock rounding)
        ready_threshold = now + timedelta(seconds=1)
        query = {
            "status": {"$in": ["pending", "running"]},
            "scheduled_at": {"$lte": ready_threshold},
            "$or": [
                {"status": "pending", "locked_at": None},
                {"status": "running", "locked_at": {"$lt": stale_threshold}},
            ],
        }

        update = {
            "$set": {
                "status": "running",
                "locked_at": now,
                "locked_by": worker_id,
                "started_at": now,
            },
            "$inc": {"attempts": 1},
        }

        # Select earliest scheduled job
        doc = await self._col.find_one_and_update(
            filter=query,
            update=update,
            sort=[("scheduled_at", ASCENDING), ("created_at", ASCENDING)],
            return_document=ReturnDocument.AFTER,
        )

        return _serialize(doc) if doc else None

    async def complete_job(
        self,
        job_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> Optional[dict]:
        """Mark a leased job as successfully completed."""
        now = _utcnow()
        doc = await self._col.find_one_and_update(
            {"_id": ObjectId(job_id)},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": now,
                    "locked_at": None,
                    "locked_by": None,
                    "result": result or {},
                    "error_message": None,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return _serialize(doc) if doc else None

    async def fail_or_retry_job(
        self,
        job_id: str,
        error_message: str,
        can_retry: bool = True,
        backoff_base_seconds: float = 2.0,
    ) -> Optional[dict]:
        """
        Handle job failure:
        - If attempts < max_retries and can_retry is True: schedule retry with exponential backoff + jitter.
        - Otherwise: mark job permanently failed.
        """
        now = _utcnow()
        current = await self._col.find_one({"_id": ObjectId(job_id)})
        if not current:
            return None

        attempts = current.get("attempts", 1)
        max_retries = current.get("max_retries", 3)

        if can_retry and attempts < max_retries:
            # Exponential backoff with jitter: 2^attempts + random(0, 1)
            backoff = (backoff_base_seconds ** attempts) + random.uniform(0.1, 1.0)
            next_schedule = now + timedelta(seconds=backoff)

            update = {
                "$set": {
                    "status": "pending",
                    "scheduled_at": next_schedule,
                    "locked_at": None,
                    "locked_by": None,
                    "error_message": f"Attempt {attempts} failed: {error_message}",
                }
            }
            logger.warning(
                "Job %s failed (attempt %d/%d), retrying in %.2fs. Error: %s",
                job_id, attempts, max_retries, backoff, error_message
            )
        else:
            update = {
                "$set": {
                    "status": "failed",
                    "completed_at": now,
                    "locked_at": None,
                    "locked_by": None,
                    "error_message": error_message,
                }
            }
            logger.error("Job %s permanently failed after %d attempts: %s", job_id, attempts, error_message)

        doc = await self._col.find_one_and_update(
            {"_id": ObjectId(job_id)},
            update,
            return_document=ReturnDocument.AFTER,
        )
        return _serialize(doc) if doc else None

    async def find_by_id(self, job_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        """Retrieve a job by ID, optionally verifying user ownership."""
        try:
            query: Dict[str, Any] = {"_id": ObjectId(job_id)}
            if user_id:
                query["user_id"] = ObjectId(user_id)
            doc = await self._col.find_one(query)
            return _serialize(doc) if doc else None
        except Exception:
            return None

    async def list_jobs(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[dict]:
        """List background jobs with filtering and pagination."""
        query: Dict[str, Any] = {}
        if user_id:
            query["user_id"] = ObjectId(user_id)
        if status:
            query["status"] = status
        if job_type:
            query["job_type"] = job_type

        cursor = self._col.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [_serialize(d) for d in docs]

    async def count_jobs(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count background jobs matching criteria."""
        query: Dict[str, Any] = {}
        if user_id:
            query["user_id"] = ObjectId(user_id)
        if status:
            query["status"] = status
        return await self._col.count_documents(query)

    async def get_queue_stats(self) -> Dict[str, int]:
        """Get aggregate counts of jobs by status for queue monitoring."""
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        counts = {"pending": 0, "running": 0, "completed": 0, "failed": 0, "cancelled": 0}
        cursor = self._col.aggregate(pipeline)
        async for item in cursor:
            status_key = item.get("_id")
            if status_key in counts:
                counts[status_key] = item.get("count", 0)

        counts["total"] = sum(counts.values())
        return counts

    async def cancel_job(self, job_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        """Cancel a pending job before execution begins."""
        now = _utcnow()
        query: Dict[str, Any] = {
            "_id": ObjectId(job_id),
            "status": "pending",
        }
        if user_id:
            query["user_id"] = ObjectId(user_id)

        doc = await self._col.find_one_and_update(
            query,
            {"$set": {"status": "cancelled", "completed_at": now}},
            return_document=ReturnDocument.AFTER,
        )
        return _serialize(doc) if doc else None
