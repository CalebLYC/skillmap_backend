from fastapi import HTTPException
from app.db.repositories.role_repository import RoleRepository
from app.models.user import UserModel


class PermissionService:
    def __init__(self, role_repos: RoleRepository):
        self.role_repos = role_repos

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
        if not await self.has_permission(user, permission_code):
            raise HTTPException(status_code=403, detail="Permission denied")
        return True
