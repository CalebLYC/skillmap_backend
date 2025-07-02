import asyncio
import datetime

from bson import ObjectId
from fastapi import Depends, HTTPException
from app.core.jwt import JWTUtils
from app.core.security import SecurityUtils
from app.db.repositories.access_token_repository import AccessTokenRepository
from app.db.repositories.user_repository import UserRepository
from app.models.access_token import AccessTokenModel
from app.schemas.auth_schema import (
    LoginRequestSchema,
    LoginResponseSchema,
    RegisterSchema,
)
from app.models.user import UserModel
from app.schemas.user import UserReadSchema


class AuthService:
    def __init__(
        self, access_token_repos: AccessTokenRepository, user_repos: UserRepository
    ):
        self.access_token_repos = access_token_repos
        self.user_repos = user_repos
        # Définir la dépendance de l'entête Authorization

    async def generate_access_token(
        self, user_id: str, expires_in_minutes: int | None = None
    ) -> str:
        expire = None
        if expires_in_minutes:
            expire = datetime.datetime.utcnow() + datetime.timedelta(
                minutes=expires_in_minutes
            )
        payload = {
            "sub": user_id,
            "exp": expire if expire else None,
            "iat": datetime.datetime.utcnow(),
        }
        token, expires_at = JWTUtils.create_access_token(
            data=payload, expires_delta=expire if expire else None
        )
        token_doc = AccessTokenModel(
            token=token,
            user_id=ObjectId(user_id),
            expires_at=expires_at,
            revoked=False,
        )
        return await self.access_token_repos.create(access_token=token_doc)

    async def login(self, user: LoginRequestSchema) -> LoginResponseSchema:
        db_user = await self.user_repos.find_by_email(email=user.email)
        if not db_user:
            raise HTTPException(status_code=404, detail="Email not found")
        is_auth = SecurityUtils.verify_password(
            hashed=db_user.password, plain=user.password
        )
        if not is_auth:
            raise HTTPException(status_code=401, detail="Wrong credentials")
        token_id = await self.generate_access_token(user_id=db_user.id)
        access_token = await self.access_token_repos.find_by_id(id=token_id)
        return_user = UserReadSchema.model_validate(db_user)
        return LoginResponseSchema(access_token=access_token, user=return_user)

    async def register(self, user: RegisterSchema) -> LoginResponseSchema:
        if user.password_confirmation:
            if user.password != user.password_confirmation:
                raise HTTPException(
                    status_code=400, detail="Password not match password confirmation"
                )
        user_doc = UserModel.model_validate(user)
        inserted_id = await self.user_repos.create(user_doc)
        db_user = await self.user_repos.find_by_id(user_id=inserted_id)
        token_id = await self.generate_access_token(user_id=db_user.id)
        access_token = await self.access_token_repos.find_by_id(id=token_id)
        return_user = UserReadSchema.model_validate(db_user)
        return LoginResponseSchema(access_token=access_token, user=return_user)

    async def logout(self, user_id: str) -> LoginResponseSchema:
        result = await self.access_token_repos.delete_by_user_id(user_id=user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return result

    """async def clean_expired_tokens():
        await mongo_db["access_tokens"].delete_many({"expires_at": {"$lt": datetime.utcnow()}})"""
