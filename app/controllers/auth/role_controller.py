from typing import List
from fastapi import APIRouter, Body, Depends, Path, status

from app.providers.auth_provider import require_permission
from app.providers.service_provider import get_role_service
from app.schemas.role import (
    AssignPermissionSchema,
    RoleReadSchema,
    RoleUpdateSchema,
    RoleCreateSchema,
)
from app.services.auth.role_service import RoleService
from app.utils.constants import http_status


router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    responses=http_status.router_responses,
    dependencies=[require_permission("role:list")],
)


@router.get(
    "/",
    response_model=List[RoleReadSchema],
    summary="List all roles",
    # dependencies=[require_permission("role:list")],
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
    dependencies=[require_permission("role:create")],
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
    dependencies=[require_permission("role:read")],
)
async def get_role(
    id: str = Path(..., min_length=24, max_length=24),
    service: RoleService = Depends(get_role_service),
):
    return await service.get_role(role_id=id)


@router.put(
    "/{id}",
    response_model=RoleReadSchema,
    summary="Update a role",
    dependencies=[require_permission("role:update")],
)
async def update_role(
    role: RoleUpdateSchema = Body(...),
    id: str = Path(..., min_length=24, max_length=24),
    service: RoleService = Depends(get_role_service),
):
    return await service.update_role(role_id=id, role_update=role)


"""@router.put(
    "/{id}/permissions",
    response_model=RoleReadSchema,
    summary="Assign permissions to role",
)
async def update_role(
    role: RoleUpdateSchema = Body(...),
    id: str = Path(..., min_length=24, max_length=24),
    service: RoleService = Depends(get_role_service),
):
    return await service.update_role(role_id=id, role_update=role)"""


@router.delete(
    "/{id}",
    summary="Delete a role",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permission("role:delete")],
)
async def delete_role(
    id: str = Path(..., min_length=24, max_length=24),
    service: RoleService = Depends(get_role_service),
):
    return await service.delete_role(role_id=id)


@router.delete(
    "/",
    summary="Delete all roles",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permission("role:delete")],
)
async def delete_all_roles(
    service: RoleService = Depends(get_role_service),
):
    return await service.delete_all_roles()


@router.patch(
    "/{id}/permissions",
    response_model=RoleReadSchema,
    summary="Add permissions to a role",
    dependencies=[require_permission("role:assign_permissions")],
)
async def add_permissions_to_role(
    body: AssignPermissionSchema,
    id: str = Path(..., min_length=24, max_length=24, description="The ID of the role"),
    service: RoleService = Depends(get_role_service),
):
    """
    Add a list of permission codes to an existing role.
    Permissions not found will result in a 400 error.
    """
    return await service.add_permissions_to_role(
        role_id=id, permissions_to_add=body.permissions
    )


@router.patch(
    "/{id}/inherit",
    response_model=RoleReadSchema,
    summary="Add an inherited role to a role",
    dependencies=[require_permission("role:assign_inherited_role")],
)
async def add_inherited_role(
    id: str = Path(
        ..., min_length=24, max_length=24, description="The ID of the main role"
    ),
    role: str = Body(..., embed=True, description="The name of the role to inherit"),
    service: RoleService = Depends(get_role_service),
):
    """
    Add an existing role to be inherited by another role.
    Includes circular dependency check.
    """
    return await service.add_inherited_role(
        role_id=id,
        inherited_role_name_to_add=role,
    )


@router.patch(
    "/{id}/permissions/remove",
    response_model=RoleReadSchema,
    summary="Remove permissions from a role",
    dependencies=[require_permission("role:remove_permissions")],
)
async def remove_permissions_from_role_endpoint(
    body: AssignPermissionSchema,
    id: str = Path(..., min_length=24, max_length=24, description="The ID of the role"),
    service: RoleService = Depends(get_role_service),
):
    """
    Removes a list of permission codes from an existing role.
    """
    return await service.remove_permissions_from_role(
        role_id=id,
        permissions_to_remove=body.permissions,
    )


@router.patch(
    "/{id}/inherit/remove",
    response_model=RoleReadSchema,
    summary="Remove an inherited role from a role",
    dependencies=[require_permission("role:remove_inherited_role")],
)
async def remove_inherited_role(
    id: str = Path(
        ..., min_length=24, max_length=24, description="The ID of the main role"
    ),
    role: str = Body(..., embed=True, description="The name of the role to inherit"),
    service: RoleService = Depends(get_role_service),
):
    """
    Removes an inherited role from an existing role.
    """
    return await service.remove_inherited_role(
        role_id=id, inherited_role_to_remove_name=role
    )
