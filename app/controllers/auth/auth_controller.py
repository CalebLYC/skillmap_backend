from fastapi import APIRouter, Depends, status

from app.core.providers.auth_provider import auth_middleware
from app.core.providers.providers import get_db
from app.db.repositories.access_token_repository import AccessTokenRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.auth_schema import (
    LoginRequestSchema,
    LoginResponseSchema,
    RegisterSchema,
)
from app.schemas.user import UserReadSchema
from app.services.auth.auth_service import AuthService


# Router
router = APIRouter(
    tags=["Auth"],
    dependencies=[],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden"},
    },
)


def get_auth_service(db=Depends(get_db)) -> AuthService:
    user_repos = UserRepository(db)
    access_token_repos = AccessTokenRepository(db)
    return AuthService(user_repos=user_repos, access_token_repos=access_token_repos)


@router.post(
    "/login",
    response_model=LoginResponseSchema,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    response_description="Login user",
)
async def login(
    user: LoginRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(user=user)


@router.post(
    "/register",
    response_model=LoginResponseSchema,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    response_description="Register user",
)
async def register(
    user: RegisterSchema,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(user=user)


@router.get(
    "/me",
    response_model=UserReadSchema,
    summary="Get the current authenticated user",
)
async def get_user(
    current_user: UserReadSchema = Depends(auth_middleware),
):
    return current_user


@router.delete("/logout", status_code=204, summary="Logout the current user")
async def delete_user(
    service: AuthService = Depends(get_auth_service),
    current_user: UserReadSchema = Depends(auth_middleware),
):
    await service.logout(user_id=current_user.id)
    return {"detail": "User deleted"}
