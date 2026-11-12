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
        """Fetch all active boards for user with projection and index-covered sorting."""
        projection = {
            "name": 1,
            "description": 1,
            "is_default": 1,
            "categories": 1,
            "created_at": 1,
            "updated_at": 1,
            "user_id": 1,
        }
        cursor = (
            self._col.find(
                {"user_id": ObjectId(user_id), "is_active": True},
                projection=projection,
            )
            .sort([("is_default", -1), ("updated_at", -1)])
        )
        return [_serialize(doc) async for doc in cursor]

    async def find_all_with_tile_counts(self, user_id: str) -> List[dict]:
        """
        Single-roundtrip aggregation pipeline that fetches all active boards
        along with their active tile counts using a correlated $lookup sub-pipeline.
        Eliminates N+1 queries entirely.
        """
        try:
            uid = ObjectId(user_id)
        except Exception:
            return []

        pipeline = [
            {"$match": {"user_id": uid, "is_active": True}},
            {"$sort": {"is_default": -1, "updated_at": -1}},
            {
                "$lookup": {
                    "from": "vocabulary_items",
                    "let": {"board_id": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$board_id", "$$board_id"]},
                                        {"$eq": ["$is_active", True]},
                                    ]
                                }
                            }
                        },
                        {"$count": "count"},
                    ],
                    "as": "tile_data",
                }
            },
            {
                "$project": {
                    "id": {"$toString": "$_id"},
                    "user_id": {"$toString": "$user_id"},
                    "name": 1,
                    "description": 1,
                    "is_default": 1,
                    "categories": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "tile_count": {
                        "$ifNull": [{"$arrayElemAt": ["$tile_data.count", 0]}, 0]
                    },
                }
            },
        ]
        cursor = self._col.aggregate(pipeline)
        boards = []
        async for doc in cursor:
            # Handle datetimes if present
            for k in ("created_at", "updated_at"):
                if k in doc and isinstance(doc[k], datetime):
                    doc[k] = doc[k].isoformat()
            boards.append(doc)
        return boards

    async def find_by_id(self, board_id: str, user_id: str) -> dict | None:
        """Find a board only if it belongs to the given user, using field projection."""
        try:
            projection = {
                "name": 1,
                "description": 1,
                "is_default": 1,
                "categories": 1,
                "created_at": 1,
                "updated_at": 1,
                "user_id": 1,
            }
            doc = await self._col.find_one(
                {
                    "_id": ObjectId(board_id),
                    "user_id": ObjectId(user_id),
                    "is_active": True,
                },
                projection=projection,
            )
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
