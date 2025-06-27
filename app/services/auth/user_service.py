from typing import Optional, List
from app.db.user_repository import UserRepository
from app.models.user import UserCreate, UserUpdate, UserInDB
from fastapi import HTTPException


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user(self, user_id: str) -> Optional[UserInDB]:
        user = await self.user_repo.find_by_id(user_id)
        if user:
            return UserInDB(**user)
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user = await self.user_repo.find_by_email(email)
        if user:
            return UserInDB(**user)
        return None

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        users = await self.user_repo.list_users(skip, limit)
        return [UserInDB(**user) for user in users]

    async def create_user(self, user_create: UserCreate) -> UserInDB:
        existing = await self.user_repo.find_by_email(user_create.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        user_dict = user_create.dict()
        user_id = await self.user_repo.create(user_dict)
        created = await self.user_repo.find_by_id(user_id)
        return UserInDB(**created)

    async def update_user(self, user_id: str, user_update: UserUpdate) -> UserInDB:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        update_data = user_update.dict(exclude_unset=True)
        if "email" in update_data:
            # Check email unique
            existing = await self.user_repo.find_by_email(update_data["email"])
            if existing and str(existing["_id"]) != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")
        success = await self.user_repo.update(user_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Update failed")
        updated = await self.user_repo.find_by_id(user_id)
        return UserInDB(**updated)

    async def delete_user(self, user_id: str) -> None:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        success = await self.user_repo.delete(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Delete failed")
