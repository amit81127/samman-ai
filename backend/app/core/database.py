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

    # Configure DNS resolver with reliable nameservers to prevent SRV lookup timeouts on Windows
    try:
        import dns.resolver
        dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
        dns.resolver.default_resolver.lifetime = 12.0
        dns.resolver.default_resolver.timeout = 6.0
    except Exception:
        pass

    last_exc = None
    for attempt in range(1, 4):
        try:
            logger.info("Connecting to MongoDB Atlas (attempt %d/3)...", attempt)
            _client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                maxIdleTimeMS=settings.MONGODB_MAX_IDLE_TIME_MS,
                serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
                connectTimeoutMS=settings.MONGODB_CONNECT_TIMEOUT_MS,
                socketTimeoutMS=settings.MONGODB_SOCKET_TIMEOUT_MS,
                waitQueueTimeoutMS=settings.MONGODB_WAIT_QUEUE_TIMEOUT_MS,
            )
            # Verify connection
            await _client.admin.command("ping")
            _database = _client[settings.DATABASE_NAME]
            logger.info("Connected to MongoDB Atlas: %s", settings.DATABASE_NAME)
            # Create indexes after connection
            try:
                await _create_indexes()
            except Exception as idx_exc:
                logger.warning("MongoDB index creation encountered non-fatal warning: %s", idx_exc)
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

    # boards — fast lookup and index-covered sorting for owner boards
    await db.boards.create_index(
        [
            ("user_id", ASCENDING),
            ("is_active", ASCENDING),
            ("is_default", DESCENDING),
            ("updated_at", DESCENDING),
        ]
    )
    await db.boards.create_index([("user_id", ASCENDING), ("is_active", ASCENDING)])

    # vocabulary_items — compound index for tile retrieval, sorting, and batch counting
    await db.vocabulary_items.create_index(
        [
            ("board_id", ASCENDING),
            ("user_id", ASCENDING),
            ("is_active", ASCENDING),
            ("position", ASCENDING),
        ]
    )
    await db.vocabulary_items.create_index(
        [("user_id", ASCENDING), ("is_active", ASCENDING), ("board_id", ASCENDING)]
    )

    # messages — compound indexes for history and cursor-based pagination
    await db.messages.create_index(
        [("user_id", ASCENDING), ("is_deleted", ASCENDING), ("_id", DESCENDING)]
    )
    await db.messages.create_index(
        [("user_id", ASCENDING), ("is_deleted", ASCENDING), ("updated_at", DESCENDING)]
    )

    # phrases — compound indexes for active phrases and cursor-based pagination
    await db.phrases.create_index(
        [("user_id", ASCENDING), ("is_active", ASCENDING), ("_id", DESCENDING)]
    )
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

    # background_jobs — queue polling, user tracking, and unique idempotency
    await db.background_jobs.create_index(
        [("status", ASCENDING), ("scheduled_at", ASCENDING), ("locked_at", ASCENDING)]
    )
    await db.background_jobs.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)]
    )
    try:
        await db.background_jobs.create_index(
            [("idempotency_key", ASCENDING)],
            unique=True,
            partialFilterExpression={"idempotency_key": {"$type": "string"}},
        )
    except Exception as exc:
        if "IndexKeySpecsConflict" in str(exc) or "86" in str(exc):
            try:
                await db.background_jobs.drop_index("idempotency_key_1")
                await db.background_jobs.create_index(
                    [("idempotency_key", ASCENDING)],
                    unique=True,
                    partialFilterExpression={"idempotency_key": {"$type": "string"}},
                )
            except Exception:
                pass

    logger.info("MongoDB indexes verified/created")
