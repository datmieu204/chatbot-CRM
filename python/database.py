from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://triduc2k3:12345@cluster0.ce37x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_DB = "mydb"

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]
