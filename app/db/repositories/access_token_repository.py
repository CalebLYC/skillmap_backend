from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo_collections import DBCollections
from app.models.AccessToken import AccessTokenModel
from app.utils.db_utils.mongo_utils import MongoCollectionOperations


class AccessTokenRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db_ops = MongoCollectionOperations(db, DBCollections.TOKENS)

    async def list_tokens(self) -> List[AccessTokenModel]:
        tokens_docs = await self._db_ops.find_many()
        return [AccessTokenModel(**doc) for doc in tokens_docs]

    async def find_by_id(self, id: str) -> AccessTokenModel:
        access_token_doc = await self._db_ops.find_one({"_id": ObjectId(id)})
        if access_token_doc:
            return AccessTokenModel(**access_token_doc)
        return None

    async def find_by_token(self, token: str) -> AccessTokenModel:
        access_token_doc = await self._db_ops.find_one({"token": token})
        if access_token_doc:
            return AccessTokenModel(**access_token_doc)
        return None

    async def find_by_token_and_user_id(
        self, token: str, user_id: str
    ) -> AccessTokenModel:
        access_token_doc = await self._db_ops.find_one(
            {"token": token, "user_id": user_id}
        )
        if access_token_doc:
            return AccessTokenModel(**access_token_doc)
        return None

    async def find_by_user_id(self, user_id: str) -> List[AccessTokenModel]:
        tokens_docs = await self._db_ops.find_many({"user_id": user_id})
        return [AccessTokenModel(**doc) for doc in tokens_docs]

    async def create(self, access_token: AccessTokenModel) -> str:
        inserted_id = await self._db_ops.insert_one(
            access_token.model_dump(by_alias=True, exclude=["id"])
        )
        return inserted_id

    async def update(self, access_token_id: str, update_data: dict) -> bool:
        modified_count = await self._db_ops.update_one(
            {"_id": ObjectId(access_token_id)}, {"$set": update_data}
        )
        return modified_count > 0

    async def delete_one(self, access_token_id: str) -> bool:
        deleted_count = await self._db_ops.delete_one(
            {"_id": ObjectId(access_token_id)}
        )
        return deleted_count > 0

    async def delete_by_token(self, token: str) -> bool:
        deleted_count = await self._db_ops.delete_one({"token": token})
        return deleted_count > 0

    async def delete_by_user_id(self, user_id: str) -> bool:
        deleted_count = await self._db_ops.delete_many({"user_id": user_id})
        return deleted_count > 0

    async def delete_all(self) -> bool:
        deleted_count = await self._db_ops.delete_many({})
        return deleted_count > 0

    async def revoke_token(self, token: str) -> bool:
        updated_count = await self._db_ops.update_one(
            {"token": token}, {"$set": {"revoked": True}}
        )
        return updated_count > 0

    async def revoke(self, id: str) -> bool:
        updated_count = await self._db_ops.update_one(
            {"_id": ObjectId(id)}, {"$set": {"revoked": True}}
        )
        return updated_count > 0
