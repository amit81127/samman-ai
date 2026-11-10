"""
Board Repository
================
MongoDB data access for boards collection.
All methods enforce user_id ownership at the query level.
"""

import logging
from datetime import datetime, timezone
from typing import List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _serialize(doc: dict) -> dict:
    """Convert ObjectId fields to strings for Pydantic serialisation."""
    if doc is None:
        return None
    result = dict(doc)
    if "_id" in result:
        result["id"] = str(result.pop("_id"))
    if "user_id" in result and isinstance(result["user_id"], ObjectId):
        result["user_id"] = str(result["user_id"])
    # Convert datetimes to ISO strings
    for key in ("created_at", "updated_at"):
        if key in result and isinstance(result[key], datetime):
            result[key] = result[key].isoformat()
    return result


class BoardRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["boards"]

    async def create(self, user_id: str, data: dict) -> dict:
        now = _utcnow()
        doc = {
            "user_id": ObjectId(user_id),
            "name": data["name"],
            "description": data.get("description"),
            "is_default": data.get("is_default", False),
            "categories": data.get("categories", []),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        # If this board is set as default, unset others
        if doc["is_default"]:
            await self._col.update_many(
                {"user_id": ObjectId(user_id)},
                {"$set": {"is_default": False}},
            )
        result = await self._col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize(doc)

    async def find_all_by_user(self, user_id: str) -> List[dict]:
        cursor = self._col.find({"user_id": ObjectId(user_id), "is_active": True})
        return [_serialize(doc) async for doc in cursor]

    async def find_by_id(self, board_id: str, user_id: str) -> dict | None:
        """Find a board only if it belongs to the given user."""
        try:
            doc = await self._col.find_one({
                "_id": ObjectId(board_id),
                "user_id": ObjectId(user_id),
                "is_active": True,
            })
            return _serialize(doc) if doc else None
        except Exception:
            return None

    async def update(self, board_id: str, user_id: str, updates: dict) -> dict | None:
        """Atomic update with optional is_default unsetting."""
        try:
            updates["updated_at"] = _utcnow()
            if updates.get("is_default"):
                await self._col.update_many(
                    {"user_id": ObjectId(user_id)},
                    {"$set": {"is_default": False}},
                )
            doc = await self._col.find_one_and_update(
                {"_id": ObjectId(board_id), "user_id": ObjectId(user_id), "is_active": True},
                {"$set": updates},
                return_document=ReturnDocument.AFTER,
            )
            return _serialize(doc) if doc else None
        except Exception:
            return None

    async def soft_delete(self, board_id: str, user_id: str) -> bool:
        try:
            result = await self._col.update_one(
                {"_id": ObjectId(board_id), "user_id": ObjectId(user_id)},
                {"$set": {"is_active": False, "updated_at": _utcnow()}},
            )
            return result.modified_count > 0
        except Exception:
            return False
