"""
Vocabulary Repository
=====================
MongoDB data access for vocabulary_items collection.
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
    if doc is None:
        return None
    result = dict(doc)
    result["id"] = str(result.pop("_id"))
    for field in ("board_id", "user_id"):
        if field in result and isinstance(result[field], ObjectId):
            result[field] = str(result[field])
    return result


class VocabularyRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["vocabulary_items"]

    async def create(self, board_id: str, user_id: str, data: dict) -> dict:
        doc = {
            "board_id": ObjectId(board_id),
            "user_id": ObjectId(user_id),
            "label": data["label"],
            "symbol_uri": data.get("symbol_uri"),
            "category": data.get("category"),
            "position": data.get("position", 0),
            "color": data.get("color"),
            "is_active": True,
        }
        result = await self._col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize(doc)

    async def find_by_board(self, board_id: str, user_id: str) -> List[dict]:
        """Return active tiles for a board, ordered by position."""
        try:
            cursor = self._col.find(
                {"board_id": ObjectId(board_id), "user_id": ObjectId(user_id), "is_active": True},
            ).sort("position", 1)
            return [_serialize(doc) async for doc in cursor]
        except Exception:
            return []

    async def find_by_id(self, item_id: str, user_id: str) -> dict | None:
        try:
            doc = await self._col.find_one({
                "_id": ObjectId(item_id),
                "user_id": ObjectId(user_id),
                "is_active": True,
            })
            return _serialize(doc) if doc else None
        except Exception:
            return None

    async def update(self, item_id: str, user_id: str, updates: dict) -> dict | None:
        """Atomic single-roundtrip update."""
        try:
            doc = await self._col.find_one_and_update(
                {"_id": ObjectId(item_id), "user_id": ObjectId(user_id), "is_active": True},
                {"$set": updates},
                return_document=ReturnDocument.AFTER,
            )
            return _serialize(doc) if doc else None
        except Exception:
            return None

    async def soft_delete(self, item_id: str, user_id: str) -> bool:
        try:
            result = await self._col.update_one(
                {"_id": ObjectId(item_id), "user_id": ObjectId(user_id)},
                {"$set": {"is_active": False}},
            )
            return result.modified_count > 0
        except Exception:
            return False

    async def count_by_board(self, board_id: str, user_id: str) -> int:
        try:
            return await self._col.count_documents({
                "board_id": ObjectId(board_id),
                "user_id": ObjectId(user_id),
                "is_active": True,
            })
        except Exception:
            return 0

    async def count_tiles_for_boards(self, board_ids: List[str], user_id: str) -> dict[str, int]:
        """
        Batch count active tiles for multiple boards in a single aggregation pipeline.
        Eliminates the N+1 query problem.
        """
        if not board_ids:
            return {}
        try:
            obj_board_ids = [ObjectId(bid) for bid in board_ids]
            pipeline = [
                {
                    "$match": {
                        "board_id": {"$in": obj_board_ids},
                        "user_id": ObjectId(user_id),
                        "is_active": True,
                    }
                },
                {
                    "$group": {
                        "_id": "$board_id",
                        "count": {"$sum": 1},
                    }
                },
            ]
            cursor = self._col.aggregate(pipeline)
            counts = {}
            async for doc in cursor:
                counts[str(doc["_id"])] = doc["count"]
            return counts
        except Exception as exc:
            logger.error("Failed to batch count tiles for boards: %s", exc)
            return {}
