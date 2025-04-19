from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI
from ..logging import LOGGER
import asyncio

LOGGER(__name__).info("Connecting to your Mongo Database...")
try:
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)
    mongodb = _mongo_async_.Anon
    LOGGER(__name__)info("Connected to your Mongo Database.")

# Get chats and users collections
    chats_collection = mongodb["chats"]
    users_collection = mongodb["tgusersdb"]

# Count documents
    chats_count = await chats_collection.count_documents({})
    users_count = await users_collection.count_documents({})

    LOGGER(__name__).info(f"Total Migrated Chats: {chats_count}")
    LOGGER(__name__).info(f"Total Migrated Users: {users_count}")

except:
    LOGGER(__name__).error(f"Failed to connect to your Mongo Database. Error: {e}")
    exit()
