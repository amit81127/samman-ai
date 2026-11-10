"""
MongoDB Database Connection
===========================
Uses Motor (async PyMongo) for non-blocking database operations.
Call connect_to_mongo() on startup, close_mongo_connection() on shutdown.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global client and database references
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    """Create MongoDB connection on application startup with retry resilience."""
    global _client, _database
    last_exc = None
    for attempt in range(1, 4):
        try:
            logger.info("Connecting to MongoDB Atlas (attempt %d/3)...", attempt)
            _client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=20000,
                connectTimeoutMS=15000,
                socketTimeoutMS=20000,
            )
            # Verify connection
            await _client.admin.command("ping")
            _database = _client[settings.DATABASE_NAME]
            logger.info("Connected to MongoDB Atlas: %s", settings.DATABASE_NAME)
            # Create indexes after connection
            await _create_indexes()
            return
        except Exception as exc:
            last_exc = exc
            logger.warning("MongoDB connection attempt %d failed: %s", attempt, exc)
            if attempt < 3:
                import asyncio
                await asyncio.sleep(1.5)

    logger.critical("Failed to connect to MongoDB after 3 attempts: %s", last_exc)
    raise last_exc


async def close_mongo_connection() -> None:
    """Close MongoDB connection on application shutdown."""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Return the active database instance. Used by repositories."""
    if _database is None:
        raise RuntimeError("Database not initialised. Call connect_to_mongo() first.")
    return _database


async def _create_indexes() -> None:
    """
    Create all required MongoDB indexes.
    Idempotent — safe to run on every startup.
    """
    db = get_database()

    # users — unique email
    await db.users.create_index([("email", ASCENDING)], unique=True)

    # communication_profiles — fast 1:1 lookup by user_id
    await db.communication_profiles.create_index([("user_id", ASCENDING)], unique=True)

    # boards — fast lookup by owner and active status
    await db.boards.create_index([("user_id", ASCENDING), ("is_active", ASCENDING)])

    # vocabulary_items — compound index for tile retrieval, sorting and aggregation
    await db.vocabulary_items.create_index(
        [
            ("board_id", ASCENDING),
            ("user_id", ASCENDING),
            ("is_active", ASCENDING),
            ("position", ASCENDING),
        ]
    )
    await db.vocabulary_items.create_index(
        [("user_id", ASCENDING), ("is_active", ASCENDING)]
    )

    # messages — compound index for history by user, ignoring deleted
    await db.messages.create_index(
        [("user_id", ASCENDING), ("is_deleted", ASCENDING), ("updated_at", DESCENDING)]
    )

    # phrases — compound index for active phrases sorted newest first
    await db.phrases.create_index(
        [("user_id", ASCENDING), ("is_active", ASCENDING), ("created_at", DESCENDING)]
    )

    # partner_permissions — exact lookup for active, non-expired delegations
    await db.partner_permissions.create_index(
        [
            ("owner_id", ASCENDING),
            ("partner_id", ASCENDING),
            ("is_active", ASCENDING),
            ("expires_at", ASCENDING),
        ]
    )
    await db.partner_permissions.create_index(
        [("owner_id", ASCENDING), ("is_active", ASCENDING), ("granted_at", DESCENDING)]
    )
    await db.partner_permissions.create_index(
        [("partner_id", ASCENDING), ("is_active", ASCENDING)]
    )

    # speech_jobs — job history per message and user
    await db.speech_jobs.create_index(
        [("message_id", ASCENDING), ("created_at", DESCENDING)]
    )
    await db.speech_jobs.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)]
    )

    logger.info("MongoDB indexes verified/created")
