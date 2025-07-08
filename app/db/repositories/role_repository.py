from typing import List
from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo_collections import DBCollections
from app.models.Role import RoleModel
from app.utils.db_utils.mongo_utils import MongoCollectionOperations


class RoleRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db_ops = MongoCollectionOperations(db, DBCollections.ROLES)

    async def find_by_name(self, name: str) -> RoleModel | None:
        data = await self._db_ops.find_one({"name": name})
        return RoleModel(**data) if data else None

    async def find_by_id(self, id: str) -> RoleModel | None:
        data = await self._db_ops.find_one({"_id": ObjectId(id)})
        return RoleModel(**data) if data else None

    async def find_many_by_names(self, names: List[str]) -> List[RoleModel]:
        docs = await self._db_ops.find_many({"name": {"$in": names}})
        return [RoleModel(**doc) for doc in docs]

    async def list_roles(self) -> List[RoleModel]:
        docs = await self._db_ops.find_many({})
        return [RoleModel(**doc) for doc in docs]

    async def create(self, role: RoleModel) -> str:
        result = await self._db_ops.insert_one(
            role.model_dump(by_alias=True, exclude=["id"])
        )
        if hasattr(result, "inserted_id") and result.inserted_id:
            new_role_id = str(result.inserted_id)
        else:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve ID of created role."
            )
        return new_role_id

    async def update(self, role_id: str, update_data: dict) -> bool:
        result = await self._db_ops.update_one(
            {"_id": ObjectId(role_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_one(self, id: str) -> bool:
        result = await self._db_ops.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def delete_one_by_name(self, name: str) -> bool:
        result = await self._db_ops.delete_one({"name": name})
        return result.deleted_count > 0

    async def delete_all(self) -> bool:
        result = await self._db_ops.delete_many({})
        return result.deleted_count > 0
