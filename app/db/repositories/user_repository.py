from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from bson import ObjectId
from app.db.mongo_collections import DBCollections
from app.models.user import UserModel
from app.utils.db_utils.mongo_utils import MongoCollectionOperations


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        # self.collection = db.get_collection(DBCollections.USERS)
        self._db_ops = MongoCollectionOperations(db, DBCollections.USERS)

    async def find_by_id(self, user_id: str) -> Optional[UserModel]:
        doc = await self._db_ops.find_one({"_id": ObjectId(user_id)})
        if doc:
            return UserModel(**doc)
        return None

    async def find_by_email(self, email: str) -> Optional[UserModel]:
        doc = await self._db_ops.find_one({"email": email})
        if doc:
            return UserModel(**doc)
        return None

    async def find_by_phone_number(self, phone_number: str) -> Optional[UserModel]:
        doc = await self._db_ops.find_one({"phone_number": phone_number})
        if doc:
            return UserModel(**doc)
        return None

    async def list_users(
        self, skip: int = 0, limit: Optional[int] = 100, all: bool = False
    ) -> List[UserModel]:
        query = {}

        effective_skip = max(0, skip)
        effective_limit = max(1, limit) if limit is not None else 100

        if all:
            docs = await self._db_ops.find_many(query=query, skip=0, limit=None)
        else:
            docs = await self._db_ops.find_many(
                query=query, skip=effective_skip, limit=effective_limit
            )

        return [UserModel.model_validate(doc) for doc in docs]

    async def create(self, user: UserModel) -> str:
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        inserted_id = await self._db_ops.insert_one(user_dict)
        return str(inserted_id)

    async def update(self, user_id: str, update_data: dict) -> bool:
        modified_count = await self._db_ops.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return modified_count > 0

    async def delete(self, user_id: str) -> bool:
        deleted_count = await self._db_ops.delete_one({"_id": ObjectId(user_id)})
        return deleted_count > 0
