from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo_collections import DBCollections
from app.models.role import RoleModel


class RoleRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.get_collection(DBCollections.ROLES)

    async def find_by_name(self, name: str) -> RoleModel | None:
        data = await self.collection.find_one({"name": name})
        return RoleModel(**data) if data else None

    async def find_by_id(self, id: str) -> RoleModel | None:
        data = await self.collection.find_one({"_id": ObjectId(id)})
        return RoleModel(**data) if data else None

    async def find_many_by_names(self, names: List[str]) -> List[RoleModel]:
        cursor = self.collection.find({"name": {"$in": names}})
        return [RoleModel(**doc) async for doc in cursor]

    async def list_roles(self) -> List[RoleModel]:
        cursor = self.collection.find({})
        return [RoleModel(**doc) async for doc in cursor]

    async def create(self, role: RoleModel) -> str:
        result = await self.collection.insert_one(
            role.model_dump(by_alias=True, exclude=["id"])
        )
        return result.inserted_id

    async def update(self, role_id: str, update_data: dict) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(role_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_one(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def delete_one_by_name(self, name: str) -> bool:
        result = await self.collection.delete_one({"name": name})
        return result.deleted_count > 0

    async def delete_all(self) -> bool:
        result = await self.collection.delete_many({})
        return result.deleted_count > 0
