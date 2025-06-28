from fastapi import APIRouter, Depends, Query, Path
from typing import List
from app.core.providers import get_db
from app.db.repositories.user_repository import UserRepository
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


def get_user_service(db=Depends(get_db)) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)


@router.get("/", response_model=List[UserReadSchema], summary="List users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    all: bool = Query(default=False),
    service: UserService = Depends(get_user_service),
):
    return await service.list_users(skip=skip, limit=limit, all=all)


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
    "/", response_model=UserReadSchema, status_code=201, summary="Create a new user"
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


@router.delete("/{user_id}", status_code=204, summary="Delete a user by ID")
async def delete_user(
    user_id: str = Path(..., min_length=24, max_length=24),
    service: UserService = Depends(get_user_service),
):
    await service.delete_user(user_id)
    return {"detail": "User deleted"}
