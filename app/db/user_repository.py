from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId
from app.db.mongo_collections import DBCollections
from app.models.user import UserModel


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.get_collection(DBCollections.USERS)

    async def find_by_id(self, user_id: str) -> Optional[UserModel]:
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if doc:
            return UserModel(**doc)
        return None

    async def find_by_email(self, email: str) -> Optional[UserModel]:
        doc = await self.collection.find_one({"email": email})
        if doc:
            return UserModel(**doc)
        return None

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        cursor = self.collection.find().skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [UserModel(**doc) for doc in docs]

    async def create(self, user: UserModel) -> str:
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(user_dict)
        return str(result.inserted_id)

    async def update(self, user_id: str, update_data: dict) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
