from typing import List
from fastapi import HTTPException
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.models.role import PermissionModel
from app.models.user import UserModel
from app.schemas.role import PermissionReadSchema, PermissionUpdateSchema


class PermissionService:
    def __init__(
        self, role_repos: RoleRepository, permission_repos: PermissionRepository
    ):
        self.role_repos = role_repos
        self.permission_repos = permission_repos

    async def get_all_permissions(self, user: UserModel) -> set[str]:
        # 1. Permissions directes
        perms = set(user.permissions)

        # 2. Permissions des rôles + hérités
        seen = set()
        to_visit = list(user.roles)

        while to_visit:
            role_name = to_visit.pop()
            if role_name in seen:
                continue
            seen.add(role_name)

            role = await self.role_repos.find_by_name(role_name)
            if not role:
                continue

            perms.update(role.permissions)
            to_visit.extend(role.inherited_roles)

        return perms

    async def has_permission(self, user: UserModel, permission_code: str) -> bool:
        all_permissions = await self.get_all_permissions(user)
        return permission_code in all_permissions

    async def ensure_permission(self, user: UserModel, permission_code: str) -> bool:
        db_permission = await self.permission_repos.find_by_code(code=permission_code)
        if not db_permission:
            raise HTTPException(status_code=500, detail="Unkown permission")
        if not await self.has_permission(user, permission_code):
            raise HTTPException(status_code=403, detail="Permission denied")
        return True

    async def get_permission_by_code(
        self, permission_code: str
    ) -> PermissionModel | None:
        try:
            return await self.permission_repos.find_by_code(code=permission_code)
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error getting permission: {str(e.detail)}",
            )

    async def get_permission(self, permission_id: str) -> PermissionModel | None:
        try:
            return await self.permission_repos.find_by_id(id=permission_id)
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error getting permission: {str(e.detail)}",
            )

    async def list_permissions(self) -> List[PermissionModel]:
        try:
            return await self.permission_repos.list_permissions()
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error getting permissions: {str(e.detail)}",
            )

    async def create_permission(self, permission: PermissionModel) -> PermissionModel:
        try:
            return await self.permission_repos.create(permission=permission)
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error creating permission: {str(e.detail)}",
            )

    async def update(
        self, permission_id: str, permission_update: PermissionUpdateSchema
    ) -> bool:
        try:
            permission = await self.permission_repos.find_by_id(id=permission_id)
            if not permission:
                raise HTTPException(status_code=404, detail="Permission not found")

            update_data = permission_update.model_dump(exclude_unset=True)
            if "code" in update_data:
                existing = await self.permission_repos.find_by_code(update_data["code"])
                if existing and str(existing.id) != permission_id:
                    raise HTTPException(
                        status_code=400, detail="Code permission already used"
                    )

            success = await self.permission_repos.update(
                id=permission_id, update_data=update_data
            )
            if not success:
                raise HTTPException(status_code=500, detail="Update failed")

            updated = await self.permission_repos.find_by_id(id=permission_id)
            return PermissionReadSchema.model_validate(updated)
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error updating permission: {str(e.detail)}",
            )

    async def delete_permission(self, permission_id: str) -> bool:
        try:
            return await self.permission_repos.delete_one(id=permission_id)
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error deleting permission: {str(e.detail)}",
            )

    async def delete_all_permissions(self) -> bool:
        try:
            return await self.permission_repos.delete_all()
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error deleting all permission: {str(e.detail)}",
            )
