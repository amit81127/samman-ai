"""
Message Repository
==================
MongoDB data access for the messages collection.
Messages are the central entity — handle with care.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

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
    if "user_id" in result and isinstance(result["user_id"], ObjectId):
        result["user_id"] = str(result["user_id"])
    for key in ("created_at", "updated_at", "approved_at"):
        if key in result and isinstance(result[key], datetime):
            result[key] = result[key].isoformat()
    return result


class MessageRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["messages"]

    async def create(
        self,
        user_id: str,
        selected_concepts: List[dict],
        literal_text: str,
        candidates: List[dict],
        model: Optional[str] = None,
        generation: Optional[dict] = None,
    ) -> dict:
        now = _utcnow()
        doc = {
            "user_id": ObjectId(user_id),
            "selected_concepts": selected_concepts,
            "literal_text": literal_text,
            "candidates": candidates,
            "model": model,
            "generation": generation,
            "approved_text": None,
            "approved_candidate_id": None,
            "approval_status": "pending",
            "approved_at": None,
            "version": 0,
            "is_deleted": False,
            "created_at": now,
            "updated_at": now,
        }
        result = await self._col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize(doc)

    async def find_by_id(self, message_id: str, user_id: str) -> Optional[dict]:
        """Return message only if it belongs to user_id, using field projection."""
        try:
            projection = {
                "selected_concepts": 1,
                "literal_text": 1,
                "candidates": 1,
                "model": 1,
                "generation": 1,
                "approved_text": 1,
                "approval_status": 1,
                "version": 1,
                "created_at": 1,
                "updated_at": 1,
                "user_id": 1,
            }
            doc = await self._col.find_one(
                {
                    "_id": ObjectId(message_id),
                    "user_id": ObjectId(user_id),
                    "is_deleted": False,
                },
                projection=projection,
            )
            return _serialize(doc) if doc else None
        except Exception:
            return None

    async def find_recent(
        self,
        user_id: str,
        limit: int = 20,
        cursor: Optional[str] = None,
    ) -> List[dict]:
        """
        Return recent messages using high-performance cursor-based pagination and projection.
        Pass cursor (last seen _id string) to fetch next page with zero skip() overhead.
        """
        try:
            query = {"user_id": ObjectId(user_id), "is_deleted": False}
            if cursor and ObjectId.is_valid(cursor):
                query["_id"] = {"$lt": ObjectId(cursor)}

            projection = {
                "selected_concepts": 1,
                "literal_text": 1,
                "candidates": 1,
                "model": 1,
                "generation": 1,
                "approved_text": 1,
                "approval_status": 1,
                "version": 1,
                "created_at": 1,
                "updated_at": 1,
                "user_id": 1,
            }
            cursor_res = (
                self._col.find(query, projection=projection)
                .sort([("_id", -1)])
                .limit(limit)
            )
            return [_serialize(doc) async for doc in cursor_res]
        except Exception as exc:
            logger.error("Error in find_recent: %s", exc)
            return []

    async def approve(
        self,
        message_id: str,
        user_id: str,
        approved_text: str,
        candidate_id: Optional[str],
    ) -> Optional[dict]:
        """
        Record an explicit user approval in a single atomic database operation.
        Atomically increments version and transitions approval_status to 'approved'.
        """
        now = _utcnow()
        try:
            doc = await self._col.find_one_and_update(
                {
                    "_id": ObjectId(message_id),
                    "user_id": ObjectId(user_id),
                    "is_deleted": False,
                },
                {
                    "$set": {
                        "approved_text": approved_text,
                        "approved_candidate_id": candidate_id,
                        "approval_status": "approved",
                        "approved_at": now,
                        "updated_at": now,
                    },
                    "$inc": {"version": 1},
                },
                return_document=ReturnDocument.AFTER,
            )
            return _serialize(doc) if doc else None
        except Exception:
            return None

    async def invalidate_approval(self, message_id: str, user_id: str) -> bool:
        """Reset approval status — called when user wants to re-edit."""
        try:
            result = await self._col.update_one(
                {"_id": ObjectId(message_id), "user_id": ObjectId(user_id)},
                {"$set": {
                    "approval_status": "pending",
                    "approved_text": None,
                    "approved_at": None,
                    "updated_at": _utcnow(),
                }},
            )
            return result.matched_count > 0
        except Exception:
            return False
