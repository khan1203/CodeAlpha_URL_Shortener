"""
MongoDB connection management using Motor (async MongoDB driver).

The connection is opened once on application startup and closed on shutdown
(see app/main.py lifespan handler), rather than opening a new connection per
request.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    """Create the Motor client and verify connectivity."""
    logger.info("Connecting to MongoDB at %s", settings.mongo_uri)
    mongodb.client = AsyncIOMotorClient(settings.mongo_uri)
    mongodb.db = mongodb.client[settings.mongo_db_name]

    # Fail fast if MongoDB is unreachable, instead of failing silently later.
    await mongodb.client.admin.command("ping")
    logger.info("Successfully connected to MongoDB (db=%s)", settings.mongo_db_name)

    await create_indexes()


async def close_mongo_connection() -> None:
    if mongodb.client is not None:
        mongodb.client.close()
        logger.info("MongoDB connection closed")


async def create_indexes() -> None:
    """Ensure short_code is unique and fast to look up."""
    await get_url_collection().create_index("short_code", unique=True)


def get_url_collection() -> AsyncIOMotorCollection:
    """Return the 'urls' collection. Raises if called before startup."""
    if mongodb.db is None:
        raise RuntimeError("Database not initialized. Did the app startup event run?")
    return mongodb.db["urls"]
