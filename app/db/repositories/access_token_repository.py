from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo_collections import DBCollections
from app.models.access_token import AccessTokenModel


class AccessTokenRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.get_collection(DBCollections.TOKENS)

    async def list_tokens(self) -> List[AccessTokenModel]:
        tokens_docs = await self.collection.find().to_list(length=None)
        return [AccessTokenModel(**doc) for doc in tokens_docs]

    async def find_by_id(self, id: str) -> AccessTokenModel:
        access_token_doc = await self.collection.find_one({"_id": ObjectId(id)})
        if access_token_doc:
            return AccessTokenModel(**access_token_doc)
        return None

    async def find_by_token(self, token: str) -> AccessTokenModel:
        access_token_doc = await self.collection.find_one({"token": token})
        if access_token_doc:
            return AccessTokenModel(**access_token_doc)
        return None

    async def find_by_token_and_user_id(
        self, token: str, user_id: str
    ) -> AccessTokenModel:
        access_token_doc = await self.collection.find_one(
            {"token": token, "user_id": user_id}
        )
        if access_token_doc:
            return AccessTokenModel(**access_token_doc)
        return None

    async def find_by_user_id(self, user_id: str) -> List[AccessTokenModel]:
        tokens_docs = await self.collection.find({"user_id": user_id}).to_list(
            length=None
        )
        return [AccessTokenModel(**doc) for doc in tokens_docs]

    async def create(self, access_token: AccessTokenModel) -> str:
        result = await self.collection.insert_one(
            access_token.model_dump(by_alias=True, exclude=["id"])
        )
        return result.inserted_id

    async def update(self, access_token_id: str, update_data: dict) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(access_token_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_one(self, access_token_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(access_token_id)})
        return result.deleted_count > 0

    async def delete_by_token(self, token: str) -> bool:
        result = await self.collection.delete_one({"token": token})
        return result.deleted_count > 0

    async def delete_by_user_id(self, user_id: str) -> bool:
        result = await self.collection.delete_many({"user_id": user_id})
        return result.deleted_count > 0

    async def delete_all(self) -> bool:
        result = await self.collection.delete_many({})
        return result.deleted_count > 0
