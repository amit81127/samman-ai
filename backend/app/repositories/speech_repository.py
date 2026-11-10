"""
Speech Repository
=================
MongoDB data access for speech_jobs collection.
Records metadata for every TTS synthesis request.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _serialize(doc: dict) -> dict:
    if doc is None:
        return None
    result = dict(doc)
    result["id"] = str(result.pop("_id"))
    for field in ("user_id", "message_id"):
        if field in result and isinstance(result[field], ObjectId):
            result[field] = str(result[field])
    for key in ("created_at", "completed_at"):
        if key in result and isinstance(result[key], datetime):
            result[key] = result[key].isoformat()
    return result


class SpeechRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["speech_jobs"]

    async def create_job(
        self,
        user_id: str,
        message_id: str,
        approved_text_snapshot: str,
    ) -> dict:
        """
        Create a speech job record.
        approved_text_snapshot stores the exact text that was sent to Gnani
        at the moment of the call — independent of any later edits.
        """
        now = _utcnow()
        doc = {
            "user_id": ObjectId(user_id),
            "message_id": ObjectId(message_id),
            "approved_text_snapshot": approved_text_snapshot,
            "provider": "gnani_timbre",
            "status": "pending",
            "error_message": None,
            "created_at": now,
            "completed_at": None,
        }
        result = await self._col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize(doc)

    async def update_status(
        self,
        job_id: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> Optional[dict]:
        try:
            updates = {
                "status": status,
                "error_message": error_message,
            }
            if status in ("completed", "failed"):
                updates["completed_at"] = _utcnow()
            doc = await self._col.find_one_and_update(
                {"_id": ObjectId(job_id)},
                {"$set": updates},
                return_document=ReturnDocument.AFTER,
            )
            return _serialize(doc) if doc else None
        except Exception as exc:
            logger.error("Failed to update speech job %s status: %s", job_id, exc)
            return None

    async def find_by_id(self, job_id: str, user_id: str) -> Optional[dict]:
        try:
            doc = await self._col.find_one({
                "_id": ObjectId(job_id),
                "user_id": ObjectId(user_id),
            })
            return _serialize(doc) if doc else None
        except Exception:
            return None
