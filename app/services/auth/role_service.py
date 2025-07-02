from typing import List
from fastapi import HTTPException
from app.db.repositories.role_repository import RoleRepository
from app.schemas.role import (
    RoleCreateSchema,
    RoleReadSchema,
    PermissionUpdateSchema,
)
from app.schemas.user import UserReadSchema


class RoleService:
    def __init__(self, role_repos: RoleRepository):
        self.role_repos = role_repos

    async def get_all_roles(self, user: UserReadSchema) -> set[str]:
        # 1. Roles directes
        roles = set(user.roles)

        # 2. Roles hérités
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

            roles.update(role.inherited_roles)
            to_visit.extend(role.inherited_roles)

        return roles

    async def has_role(self, user: UserReadSchema, role_name: str) -> bool:
        all_roles = await self.get_all_roles(user)
        return role_name in all_roles

    async def ensure_role(self, user: UserReadSchema, role_name: str) -> bool:
        db_role = await self.role_repos.find_by_name(name=role_name)
        if not db_role:
            raise HTTPException(status_code=500, detail="Unkown role")
        if not await self.has_role(user, role_name):
            raise HTTPException(status_code=403, detail="Unauthorized")
        return True

    async def get_role_by_code(self, role_name: str) -> RoleReadSchema | None:
        try:
            role = await self.role_repos.find_by_name(name=role_name)
            if not role:
                raise HTTPException(
                    status_code=404,
                    detail="Role not found",
                )
            return RoleReadSchema.model_validate(role)
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error getting role: {str(e.detail)}",
            )

    async def get_role(self, role_id: str) -> RoleReadSchema | None:
        try:
            role = await self.role_repos.find_by_id(id=role_id)
            if not role:
                raise HTTPException(
                    status_code=404,
                    detail="Role not found",
                )
            return RoleReadSchema.model_validate(role)
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error getting role: {str(e.detail)}",
            )

    async def list_roles(self) -> List[RoleReadSchema]:
        try:
            roles = await self.role_repos.list_roles()
            return [RoleReadSchema.model_validate(r) for r in roles]
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while creating role: {str(e)}",
            )

    async def create_role(self, role: RoleCreateSchema) -> RoleReadSchema:
        """
        Creates a new role in the database.

        Args:
            role (RoleCreateSchema): The data for the new role.

        Returns:
            RoleReadSchema: The newly created role.

        Raises:
            HTTPException: If the role already exists or an inherited role does not exist.
        """
        try:
            # 1. Check if role name already exists
            db_role = await self.role_repos.find_by_name(name=role.name)
            if db_role:
                raise HTTPException(status_code=400, detail="Role already created")

            # 2. Validate inherited roles if provided
            if role.inherited_roles:
                existing_role_names = {
                    r.name for r in await self.role_repos.list_roles()
                }

                for inherited_role_name in role.inherited_roles:
                    if inherited_role_name not in existing_role_names:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Role '{inherited_role_name}' not found. Please create it first.",
                        )

            # 3. Create the role in the repository
            inserted_id = await self.role_repos.create(role=role)

            # 4. Fetch the newly created role by its ID
            created_role_model = await self.role_repos.find_by_id(id=inserted_id)

            if not created_role_model:
                raise HTTPException(
                    status_code=500, detail="Created role not found after insertion."
                )

            # 5. Validate and return the created role using the RoleReadSchema
            return RoleReadSchema.model_validate(created_role_model)

        except HTTPException as e:
            # Re-raise HTTPExceptions directly
            raise e
        except Exception as e:
            # Catch any other unexpected exceptions and return a 500
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while creating role: {str(e)}",
            )

    async def update_role(
        self, role_id: str, role_update: PermissionUpdateSchema
    ) -> bool:
        try:
            role = await self.role_repos.find_by_id(id=role_id)
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")

            update_data = role_update.model_dump(exclude_unset=True)
            if "name" in update_data:
                existing = await self.role_repos.find_by_name(update_data["name"])
                if existing and str(existing.id) != role_id:
                    raise HTTPException(
                        status_code=400, detail="Role name already used"
                    )

            success = await self.role_repos.update(id=role_id, update_data=update_data)
            if not success:
                raise HTTPException(status_code=500, detail="Update failed")

            updated = await self.role_repos.find_by_id(id=role_id)
            return RoleReadSchema.model_validate(updated)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while creating role: {str(e)}",
            )

    async def delete_role(self, role_id: str) -> None:
        try:
            role = await self.role_repos.find_by_id(id=role_id)
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")
            success = await self.role_repos.delete_one(id=role_id)
            if not success:
                raise HTTPException(status_code=500, detail="Delete failed")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while creating role: {str(e)}",
            )

    async def delete_all_roles(self) -> None:
        try:
            success = await self.role_repos.delete_all()
            if not success:
                raise HTTPException(status_code=500, detail="Delete failed")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while creating role: {str(e)}",
            )
