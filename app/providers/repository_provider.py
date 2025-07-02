from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.providers.providers import get_db
from app.db.repositories.access_token_repository import AccessTokenRepository
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository


def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_db)):
    return UserRepository(db=db)


def get_role_repository(db: AsyncIOMotorDatabase = Depends(get_db)):
    return RoleRepository(db=db)


def get_permission_repository(db: AsyncIOMotorDatabase = Depends(get_db)):
    return PermissionRepository(db=db)


def get_access_token_repository(db: AsyncIOMotorDatabase = Depends(get_db)):
    return AccessTokenRepository(db=db)
