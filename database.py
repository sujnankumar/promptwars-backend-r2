import motor.motor_asyncio
from pymongo.collection import Collection

MONGO_DETAILS = "mongodb+srv://sujnan:sujnan10@cluster0.2pgem1b.mongodb.net/?tls=true"
DATABASE_NAME = "promptwars-r2"
USERS_COLLECTION = "users"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client[DATABASE_NAME]

def get_users_collection() -> Collection:
    return database[USERS_COLLECTION]
