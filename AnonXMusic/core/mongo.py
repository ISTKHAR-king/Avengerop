from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI
from ..logging import LOGGER

logger = LOGGER(__name__)

logger.info("Connecting to your Mongo Database...")
try:
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)
    mongodb = _mongo_async_.Anon
    logger.info("Connected to your Mongo Database.")
except Exception as e:
    logger.error(f"Failed to connect to your Mongo Database. Error: {e}")
    exit()

# Optional: utility async function to fetch chat and user counts
async def get_mongo_stats():
    chats_collection = mongodb["chats"]
    users_collection = mongodb["tgusersdb"]

    chats_count = await chats_collection.count_documents({})
    users_count = await users_collection.count_documents({})

    return chats_count, users_count
