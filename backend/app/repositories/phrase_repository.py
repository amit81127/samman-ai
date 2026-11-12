"""
Phrase Repository
=================
MongoDB data access for phrases collection.
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
    for key in ("created_at", "updated_at"):
        if key in result and isinstance(result[key], datetime):
            result[key] = result[key].isoformat()
    return result


class PhraseRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["phrases"]

    async def create(self, user_id: str, data: dict) -> dict:
        now = _utcnow()
        doc = {
            "user_id": ObjectId(user_id),
            "text": data["text"],
            "label": data.get("label"),
            "language": data.get("language", "en"),
            "source": data.get("source", "manual"),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        result = await self._col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize(doc)

    async def find_all_by_user(
        self,
        user_id: str,
        limit: int = 50,
        cursor: Optional[str] = None,
    ) -> List[dict]:
        """Fetch saved phrases with field projection and cursor-based pagination."""
        try:
            query = {"user_id": ObjectId(user_id), "is_active": True}
            if cursor and ObjectId.is_valid(cursor):
                query["_id"] = {"$lt": ObjectId(cursor)}

            projection = {
                "text": 1,
                "label": 1,
                "language": 1,
                "source": 1,
                "is_active": 1,
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
            logger.error("Error in find_all_by_user: %s", exc)
            return []

    async def find_by_id(self, phrase_id: str, user_id: str) -> Optional[dict]:
        """Fetch a specific phrase with field projection."""
        try:
            projection = {
                "text": 1,
                "label": 1,
                "language": 1,
                "source": 1,
                "is_active": 1,
                "created_at": 1,
                "updated_at": 1,
                "user_id": 1,
            }
            doc = await self._col.find_one(
                {
                    "_id": ObjectId(phrase_id),
                    "user_id": ObjectId(user_id),
                    "is_active": True,
                },
                projection=projection,
            )
            return _serialize(doc) if doc else None
        except Exception:
            return None

    async def update(self, phrase_id: str, user_id: str, updates: dict) -> Optional[dict]:
        """Atomic single-roundtrip update."""
        try:
            updates["updated_at"] = _utcnow()
            doc = await self._col.find_one_and_update(
                {"_id": ObjectId(phrase_id), "user_id": ObjectId(user_id), "is_active": True},
                {"$set": updates},
                return_document=ReturnDocument.AFTER,
            )
            return _serialize(doc) if doc else None
        except Exception:
            return None

    async def soft_delete(self, phrase_id: str, user_id: str) -> bool:
        try:
            result = await self._col.update_one(
                {"_id": ObjectId(phrase_id), "user_id": ObjectId(user_id)},
                {"$set": {"is_active": False, "updated_at": _utcnow()}},
            )
            return result.modified_count > 0
        except Exception:
            return False
