from typing import Optional, List
from app.core.security import SecurityUtils
from app.db.repositories.user_repository import UserRepository
from app.models.User import UserModel
from app.schemas.user import UserCreateSchema, UserUpdateSchema, UserReadSchema
from fastapi import HTTPException


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user(self, user_id: str) -> Optional[UserReadSchema]:
        user = await self.user_repo.find_by_id(user_id)
        if user:
            return UserReadSchema.model_validate(user)
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserReadSchema]:
        user = await self.user_repo.find_by_email(email)
        if user:
            return UserReadSchema.model_validate(user)
        return None

    async def list_users(
        self, skip: int = 0, limit: int = 100, all: bool = False
    ) -> List[UserReadSchema]:
        users = await self.user_repo.list_users(skip=skip, limit=limit, all=all)
        return [UserReadSchema.model_validate(u) for u in users]

    async def create_user(self, user_create: UserCreateSchema) -> UserReadSchema:
        existing = await self.user_repo.find_by_email(user_create.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = SecurityUtils.hash_password(user_create.password)
        user_model = UserModel(
            **user_create.model_dump(exclude=["password"]), password=hashed_pw
        )
        user_id = await self.user_repo.create(user_model)
        created = await self.user_repo.find_by_id(user_id)
        return UserReadSchema.model_validate(created)

    async def update_user(
        self, user_id: str, user_update: UserUpdateSchema
    ) -> UserReadSchema:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user_update.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing = await self.user_repo.find_by_email(update_data["email"])
            if existing and str(existing.id) != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")

        if "password" in update_data:
            update_data["hashed_password"] = SecurityUtils.hash_password(
                update_data.pop("password")
            )

        success = await self.user_repo.update(user_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Update failed")

        updated = await self.user_repo.find_by_id(user_id)
        return UserReadSchema.model_validate(updated)

    async def delete_user(self, user_id: str) -> None:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        success = await self.user_repo.delete(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Delete failed")
        return success
