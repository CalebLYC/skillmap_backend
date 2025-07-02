from typing import List
from fastapi import APIRouter, Body, Depends, Path, status

from app.providers.service_provider import get_role_service
from app.schemas.role import (
    RoleReadSchema,
    RoleUpdateSchema,
    RoleCreateSchema,
)
from app.services.auth.role_service import RoleService


router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden"},
    },
)


@router.get(
    "/",
    response_model=List[RoleReadSchema],
    summary="List all roles",
)
async def list_roles(
    service: RoleService = Depends(get_role_service),
):
    return await service.list_roles()


@router.post(
    "/",
    response_model=RoleReadSchema,
    summary="Create a role",
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    role: RoleCreateSchema = Body(...),
    service: RoleService = Depends(get_role_service),
):
    return await service.create_role(role=role)


@router.get(
    "/{id}",
    response_model=RoleReadSchema,
    summary="Get a role",
)
async def get_role(
    id: str = Path(..., min_length=24, max_length=24),
    service: RoleService = Depends(get_role_service),
):
    return await service.get_role(role_id=id)


@router.put(
    "/{id}",
    response_model=RoleReadSchema,
    summary="Get a role",
)
async def update_role(
    role: RoleUpdateSchema = Body(...),
    id: str = Path(..., min_length=24, max_length=24),
    service: RoleService = Depends(get_role_service),
):
    return await service.update_role(role_id=id, role_update=role)


@router.delete("/{id}", summary="Delete a role", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    id: str = Path(..., min_length=24, max_length=24),
    service: RoleService = Depends(get_role_service),
):
    return await service.delete_role(role_id=id)


@router.delete("/", summary="Delete all roles", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_roles(
    service: RoleService = Depends(get_role_service),
):
    return await service.delete_all_roles()
