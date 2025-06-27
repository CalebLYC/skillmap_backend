# db/mongo_client.py
from motor.motor_asyncio import AsyncIOMotorClient


class MongoClient:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    def get_db(self):
        return self.db
