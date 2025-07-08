from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo_collections import DBCollections
from app.models.Role import PermissionModel
from app.utils.db_utils.mongo_utils import MongoCollectionOperations


class PermissionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db_ops = MongoCollectionOperations(db, DBCollections.PERMISSIONS)

    async def find_by_code(self, code: str) -> PermissionModel | None:
        data = await self._db_ops.find_one({"code": code})
        return PermissionModel(**data) if data else None

    async def find_by_id(self, id: str) -> PermissionModel | None:
        data = await self._db_ops.find_one({"_id": ObjectId(id)})
        return PermissionModel(**data) if data else None

    async def find_many_by_codes(self, codes: List[str]) -> List[PermissionModel]:
        docs = await self._db_ops.find_many({"code": {"$in": codes}})
        return [PermissionModel(**doc) for doc in docs]

    async def list_permissions(self) -> List[PermissionModel]:
        docs = await self._db_ops.find_many({})
        return [PermissionModel(**doc) for doc in docs]

    async def create(self, permission: PermissionModel) -> str:
        inserted_id = await self._db_ops.insert_one(
            permission.model_dump(by_alias=True, exclude=["id"])
        )
        return inserted_id

    async def update(self, id: str, update_data: dict) -> bool:
        modified_count = await self._db_ops.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        return modified_count > 0

    async def delete_one(self, id: str) -> bool:
        deleted_count = await self._db_ops.delete_one({"_id": ObjectId(id)})
        return deleted_count > 0

    async def delete_one_by_code(self, code: str) -> bool:
        deleted_count = await self._db_ops.delete_one({"code": code})
        return deleted_count > 0

    async def delete_all(self) -> bool:
        deleted_count = await self._db_ops.delete_many({})
        return deleted_count > 0
