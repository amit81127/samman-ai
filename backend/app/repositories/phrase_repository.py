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

    async def find_all_by_user(self, user_id: str) -> List[dict]:
        cursor = self._col.find(
            {"user_id": ObjectId(user_id), "is_active": True}
        ).sort("created_at", -1)
        return [_serialize(doc) async for doc in cursor]

    async def find_by_id(self, phrase_id: str, user_id: str) -> Optional[dict]:
        try:
            doc = await self._col.find_one({
                "_id": ObjectId(phrase_id),
                "user_id": ObjectId(user_id),
                "is_active": True,
            })
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
