"""
User Repository
===============
All MongoDB data access for the users and communication_profiles collections.
No business logic here — only data access.
"""

import logging
from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._users = db["users"]
        self._profiles = db["communication_profiles"]

    # ── Users ─────────────────────────────────────────────────────────────

    async def find_by_email(self, email: str) -> dict | None:
        """Return full user document (including password_hash) or None."""
        return await self._users.find_one({"email": email.lower()})

    async def find_by_id(self, user_id: str, include_password: bool = False) -> dict | None:
        """Return user document by ObjectId string or None, excluding password_hash by default."""
        try:
            projection = None if include_password else {"password_hash": 0}
            return await self._users.find_one({"_id": ObjectId(user_id)}, projection=projection)
        except Exception:
            return None

    async def create_user(
        self, email: str, password_hash: str, language: str = "en"
    ) -> dict:
        """
        Insert a new user. Returns the created document.
        Raises DuplicateKeyError if email already exists.
        """
        now = _utcnow()
        doc = {
            "email": email.lower(),
            "password_hash": password_hash,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        try:
            result = await self._users.insert_one(doc)
            doc["_id"] = result.inserted_id
            # Create default profile
            await self._create_default_profile(str(result.inserted_id), language)
            return doc
        except DuplicateKeyError:
            raise

    async def _create_default_profile(self, user_id: str, language: str) -> None:
        """Create a default communication profile when a new user registers."""
        now = _utcnow()
        await self._profiles.insert_one({
            "user_id": ObjectId(user_id),
            "language": language,
            "voice_preference": None,
            "tile_size": "medium",
            "text_size": "normal",
            "contrast_mode": False,
            "reduced_motion": False,
            "updated_at": now,
        })

    # ── Communication Profiles ────────────────────────────────────────────

    async def get_profile(self, user_id: str) -> dict | None:
        try:
            profile = await self._profiles.find_one({"user_id": ObjectId(user_id)})
            if not profile:
                await self._create_default_profile(user_id, "en")
                profile = await self._profiles.find_one({"user_id": ObjectId(user_id)})
            return profile
        except Exception:
            return None

    async def update_profile(self, user_id: str, updates: dict) -> dict | None:
        """Apply partial updates to a user's communication profile in a single atomic roundtrip."""
        try:
            updates["updated_at"] = _utcnow()
            return await self._profiles.find_one_and_update(
                {"user_id": ObjectId(user_id)},
                {"$set": updates},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        except Exception:
            return None
