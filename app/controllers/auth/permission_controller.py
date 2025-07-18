from typing import List
from fastapi import APIRouter, Body, Depends, Path, status

from app.providers.auth_provider import require_role
from app.providers.service_provider import get_permission_service
from app.schemas.role import (
    PermissionCreateSchema,
    PermissionReadSchema,
    PermissionUpdateSchema,
)
from app.services.auth.permission_service import PermissionService
from app.utils.constants import http_status


router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    dependencies=[require_role("admin")],
    responses=http_status.router_responses,
)


@router.get(
    "/",
    response_model=List[PermissionReadSchema],
    summary="List all permissions",
)
async def list_permissions(
    service: PermissionService = Depends(get_permission_service),
):
    return await service.list_permissions()


@router.post(
    "/",
    response_model=PermissionReadSchema,
    summary="Create a permission",
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    permission: PermissionCreateSchema = Body(...),
    service: PermissionService = Depends(get_permission_service),
):
    return await service.create_permission(permission=permission)


@router.get(
    "/{id}",
    response_model=PermissionReadSchema,
    summary="Get a permission",
)
async def get_permission(
    id: str = Path(..., min_length=24, max_length=24),
    service: PermissionService = Depends(get_permission_service),
):
    return await service.get_permission(permission_id=id)


@router.put(
    "/{id}",
    response_model=PermissionReadSchema,
    summary="Update a permission",
)
async def update_permission(
    permission: PermissionUpdateSchema = Body(...),
    id: str = Path(..., min_length=24, max_length=24),
    service: PermissionService = Depends(get_permission_service),
):
    return await service.update_permission(
        permission_id=id, permission_update=permission
    )


@router.delete(
    "/{id}", summary="Delete a permission", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_permission(
    id: str = Path(..., min_length=24, max_length=24),
    service: PermissionService = Depends(get_permission_service),
):
    return await service.delete_permission(permission_id=id)


@router.delete(
    "/", summary="Delete all permissions", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_all_permissions(
    service: PermissionService = Depends(get_permission_service),
):
    return await service.delete_all_permissions()
