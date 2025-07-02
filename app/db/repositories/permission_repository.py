from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo_collections import DBCollections
from app.models.Role import PermissionModel


class PermissionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.get_collection(DBCollections.PERMISSIONS)

    async def find_by_code(self, code: str) -> PermissionModel | None:
        data = await self.collection.find_one({"code": code})
        return PermissionModel(**data) if data else None

    async def find_by_id(self, id: str) -> PermissionModel | None:
        data = await self.collection.find_one({"_id": ObjectId(id)})
        return PermissionModel(**data) if data else None

    async def find_many_by_codes(self, codes: List[str]) -> List[PermissionModel]:
        cursor = self.collection.find({"code": {"$in": codes}})
        return [PermissionModel(**doc) async for doc in cursor]

    async def list_permissions(self) -> List[PermissionModel]:
        cursor = self.collection.find({})
        return [PermissionModel(**doc) async for doc in cursor]

    async def create(self, permission: PermissionModel) -> str:
        result = await self.collection.insert_one(
            permission.model_dump(by_alias=True, exclude=["id"])
        )
        return result.inserted_id

    async def update(self, id: str, update_data: dict) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_one(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def delete_one_by_code(self, code: str) -> bool:
        result = await self.collection.delete_one({"code": code})
        return result.deleted_count > 0

    async def delete_all(self) -> bool:
        result = await self.collection.delete_many({})
        return result.deleted_count > 0
