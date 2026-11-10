"""
Partner Repository
==================
MongoDB data access for partner_permissions collection.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _serialize(doc: dict) -> dict:
    if doc is None:
        return None
    result = dict(doc)
    result["id"] = str(result.pop("_id"))
    for field in ("owner_id", "partner_id"):
        if field in result and isinstance(result[field], ObjectId):
            result[field] = str(result[field])
    for key in ("granted_at", "expires_at"):
        if key in result and isinstance(result[key], datetime):
            result[key] = result[key].isoformat()
    return result


class PartnerRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["partner_permissions"]

    async def grant(
        self,
        owner_id: str,
        partner_id: str,
        permissions: List[str],
        expires_at: datetime,
        partner_name: Optional[str] = None,
        partner_email: Optional[str] = None,
        relationship: Optional[str] = "Family member",
    ) -> dict:
        now = _utcnow()
        doc = {
            "owner_id": ObjectId(owner_id),
            "partner_id": ObjectId(partner_id) if ObjectId.is_valid(partner_id) else partner_id,
            "partner_name": partner_name,
            "partner_email": partner_email,
            "relationship": relationship or "Family member",
            "permissions": permissions,
            "granted_at": now,
            "expires_at": expires_at,
            "is_active": True,
        }
        result = await self._col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize(doc)

    async def find_by_owner(self, owner_id: str) -> List[dict]:
        try:
            cursor = self._col.find({
                "owner_id": ObjectId(owner_id),
                "is_active": True,
            }).sort("granted_at", -1)
            return [_serialize(doc) async for doc in cursor]
        except Exception:
            return []

    async def find_active_permission(self, owner_id: str, partner_id: str) -> Optional[dict]:
        try:
            now = _utcnow()
            doc = await self._col.find_one({
                "owner_id": ObjectId(owner_id),
                "partner_id": ObjectId(partner_id) if ObjectId.is_valid(partner_id) else partner_id,
                "is_active": True,
                "expires_at": {"$gt": now},
            })
            return _serialize(doc) if doc else None
        except Exception:
            return None

    async def revoke(self, permission_id: str, owner_id: str) -> bool:
        try:
            result = await self._col.update_one(
                {"_id": ObjectId(permission_id), "owner_id": ObjectId(owner_id)},
                {"$set": {"is_active": False}},
            )
            return result.modified_count > 0
        except Exception:
            return False
