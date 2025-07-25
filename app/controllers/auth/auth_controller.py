from fastapi import APIRouter, Depends, status

from app.providers.auth_provider import auth_middleware
from app.providers.service_provider import get_auth_service
from app.models.User import UserModel
from app.schemas.auth_schema import (
    LoginRequestSchema,
    LoginResponseSchema,
    RegisterSchema,
    ResetUserPasswordSchema,
)
from app.schemas.user import UserReadSchema
from app.services.auth.auth_service import AuthService
from app.utils.constants import http_status


# Router
router = APIRouter(
    tags=["Auth"],
    dependencies=[],
    responses=http_status.router_responses,
)


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
    current_user: UserModel = Depends(auth_middleware),
):
    return UserReadSchema.model_validate(current_user)


@router.delete(
    "/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Logout the current user"
)
async def delete_user(
    service: AuthService = Depends(get_auth_service),
    current_user: UserReadSchema = Depends(auth_middleware),
):
    await service.logout(user_id=current_user.id)
    return {"detail": "User deleted"}


@router.post(
    "/user/password/reset",
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Reset a user password.",
)
async def verify_otp_endpoint(
    user_request: ResetUserPasswordSchema,
    service: AuthService = Depends(get_auth_service),
):
    """
    Verifies the provided OTP code for a given email address and the reset the password.
    """
    return await service.reset_user_password(user_request=user_request)
