from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId

from app.db.mongo_collections import DBCollections


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.get_collection(DBCollections.USERS)

    async def find_by_id(self, user_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(user_id)})

    async def find_by_email(self, email: str) -> Optional[dict]:
        return await self.collection.find_one({"email": email})

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[dict]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def create(self, user_data: dict) -> str:
        result = await self.collection.insert_one(user_data)
        return str(result.inserted_id)

    async def update(self, user_id: str, update_data: dict) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
