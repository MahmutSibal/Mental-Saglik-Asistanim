from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from ..core.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None

async def connect_to_mongo():
    global _client, _db
    _client = AsyncIOMotorClient(settings.MONGODB_URI)
    _db = _client[settings.MONGODB_DB]

async def close_mongo_connection():
    global _client
    if _client:
        _client.close()


def get_db() -> AsyncIOMotorDatabase:
    assert _db is not None, "Database not initialized."
    return _db


def users_collection():
    return get_db()["users"]


def messages_collection():
    return get_db()["messages"]


def suggestions_collection():
    return get_db()["suggestions"]


def checkins_collection():
    return get_db()["checkins"]


def feedback_collection():
    return get_db()["feedback"]
