from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://dungmount75:taidungmongodb@cluster0.trr2wud.mongodb.net/chatboxcrm?retryWrites=true&w=majority"
MONGO_DB = "chatboxcrm"

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]
