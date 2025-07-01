from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.jwt import JWTUtils
from app.core.providers.providers import (
    get_access_token_repository,
    get_db,
    get_user_repository,
)
from app.db.repositories.access_token_repository import AccessTokenRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.user import UserReadSchema


oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_token(
    token: str = Depends(oauth_2_scheme),
    access_token_repos: AccessTokenRepository = Depends(get_access_token_repository),
) -> str:
    try:
        payload = JWTUtils.decode_access_token(token=token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        access_token = await access_token_repos.find_by_token_and_user_id(
            user_id=user_id, token=token
        )
        if not access_token:
            raise HTTPException(status_code=401, detail="Expired")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def auth_middleware(
    user_id: str = Depends(verify_token),
    user_repos: UserRepository = Depends(get_user_repository),
) -> UserReadSchema:
    try:
        user = await user_repos.find_by_id(user_id=user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return UserReadSchema.model_validate(user)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Error while getting user")
