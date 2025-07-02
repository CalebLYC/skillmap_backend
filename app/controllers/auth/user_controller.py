from fastapi import APIRouter, Depends, Query, Path, status
from typing import List
from app.providers.auth_provider import auth_middleware, require_permission
from app.providers.service_provider import get_user_service
from app.models.User import UserModel
from app.schemas.user import UserCreateSchema, UserUpdateSchema, UserReadSchema
from app.services.auth.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden"},
    },
)


@router.get(
    "/",
    response_model=List[UserReadSchema],
    summary="List users",
    dependencies=[require_permission("user:read")],
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    all: bool = Query(default=False),
    service: UserService = Depends(get_user_service),
):
    return await service.list_users(skip=skip, limit=limit, all=all)


@router.get(
    "/current",
    response_model=UserReadSchema,
    summary="Get the current authenticated user",
)
async def get_user(
    current_user: UserModel = Depends(auth_middleware),
):
    return UserReadSchema.model_validate(current_user)


@router.get("/{user_id}", response_model=UserReadSchema, summary="Get a user by ID")
async def get_user(
    user_id: str = Path(..., min_length=24, max_length=24),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user(user_id)
    if not user:
        return {"detail": "User not found"}
    return user


@router.post(
    "/",
    response_model=UserReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    user_create: UserCreateSchema,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(user_create)


@router.put("/{user_id}", response_model=UserReadSchema, summary="Update a user by ID")
async def update_user(
    user_id: str = Path(..., min_length=24, max_length=24),
    user_update: UserUpdateSchema = ...,
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(user_id, user_update)


@router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user by ID"
)
async def delete_user(
    user_id: str = Path(..., min_length=24, max_length=24),
    service: UserService = Depends(get_user_service),
):
    await service.delete_user(user_id)
    return {"detail": "User deleted"}
