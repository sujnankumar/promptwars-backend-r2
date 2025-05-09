import motor.motor_asyncio
from pymongo.collection import Collection

MONGO_DETAILS = "mongodb://localhost:27017"
DATABASE_NAME = "promptwars"
COLLECTION_NAME = "items"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client[DATABASE_NAME]


def get_collection() -> Collection:
    return database[COLLECTION_NAME]
