from functools import lru_cache

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings
from app.db.mongo_client import MongoClient
from app.db.repositories.access_token_repository import AccessTokenRepository
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository
from app.services.auth.permission_service import PermissionService


@lru_cache()
def get_settings():
    return Settings()


def get_db(settings: Settings = Depends(get_settings)):
    mongo = MongoClient(settings.database_uri, settings.database_name)
    return mongo.get_db()


def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_db)):
    return UserRepository(db=db)


def get_role_repository(db: AsyncIOMotorDatabase = Depends(get_db)):
    return RoleRepository(db=db)


def get_access_token_repository(db: AsyncIOMotorDatabase = Depends(get_db)):
    return AccessTokenRepository(db=db)


def get_permission_service(
    role_repos: RoleRepository = Depends(get_role_repository),
) -> PermissionService:
    return PermissionService(role_repos)
