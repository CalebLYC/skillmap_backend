from typing import List, Set
from fastapi import HTTPException
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.schemas.role_schema import (
    RoleCreateSchema,
    RoleReadSchema,
    RoleUpdateSchema,
)
from app.schemas.user_schema import UserReadSchema


class RoleService:
    def __init__(
        self, role_repos: RoleRepository, permission_repos: PermissionRepository
    ):
        self.role_repos = role_repos
        self.permission_repos = permission_repos

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

    async def get_role_by_name(self, role_name: str) -> RoleReadSchema | None:
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
                    # Circular dependency check
                    if await self._check_circular_inheritance(
                        start_role_name=inherited_role_name,
                        target_role_name=role.name,
                    ):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Circular inheritance detected: '{role.name}' cannot inherit '{inherited_role_name}' as it would create a loop.",
                        )

            if role.permissions:
                db_permission_codes = {
                    p.code for p in await self.permission_repos.list_permissions()
                }
                for permission_code in role.permissions:
                    if permission_code not in db_permission_codes:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Permission '{permission_code}' not found. Please create it first.",
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

    async def update_role(self, role_id: str, role_update: RoleUpdateSchema) -> bool:
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

            if role_update.inherited_roles:
                existing_role_names = {
                    r.name for r in await self.role_repos.list_roles()
                }

                for inherited_role_name in role_update.inherited_roles:
                    if inherited_role_name not in existing_role_names:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Role '{inherited_role_name}' not found. Please create it first.",
                        )
                    # Circular dependency check
                    if await self._check_circular_inheritance(
                        start_role_name=inherited_role_name,
                        target_role_name=role.name,
                    ):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Circular inheritance detected: '{role.name}' cannot inherit '{inherited_role_name}' as it would create a loop.",
                        )

            if role_update.permissions:
                db_permission_codes = {
                    p.code for p in await self.permission_repos.list_permissions()
                }
                for permission_code in role_update.permissions:
                    if permission_code not in db_permission_codes:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Permission '{permission_code}' not found. Please create it first.",
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

    async def add_permissions_to_role(
        self, role_id: str, permissions_to_add: List[str]
    ) -> RoleReadSchema:
        """
        Assigns new permissions to an existing role.

        Args:
            role_id (str): The id of the role to update.
            permissions_to_add (List[str]): A list of permission codes to add.

        Returns:
            RoleReadSchema: The updated role.

        Raises:
            HTTPException: If the role is not found or any permission is invalid.
        """
        try:
            role = await self.role_repos.find_by_id(id=role_id)
            if not role:
                raise HTTPException(
                    status_code=404, detail=f"Role '{role_id}' not found."
                )

            # Validate if all permissions to add actually exist
            existing_permissions = await self.permission_repos.find_many_by_codes(
                codes=permissions_to_add
            )
            existing_permission_codes = {p.code for p in existing_permissions}
            # print(f"print {existing_permission_codes}")

            for perm_code in permissions_to_add:
                if perm_code not in existing_permission_codes:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Permission '{perm_code}' not found. Please create it first.",
                    )

            # Convert current permissions to a set to easily add new ones and remove duplicates
            current_permissions = set(role.permissions)
            current_permissions.update(permissions_to_add)

            update_data = {"permissions": list(current_permissions)}
            updated = await self.role_repos.update(
                id=str(role.id), update_data=update_data
            )

            if not updated:
                raise HTTPException(
                    status_code=500, detail="Failed to update role permissions."
                )

            # Fetch and return the updated role
            updated_role_model = await self.role_repos.find_by_id(id=str(role.id))
            if not updated_role_model:
                raise HTTPException(
                    status_code=500, detail="Updated role not found after update."
                )

            return RoleReadSchema.model_validate(updated_role_model)

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while adding permissions: {str(e)}",
            )

    async def add_inherited_role(
        self, role_id: str, inherited_role_name_to_add: str
    ) -> RoleReadSchema:
        """
        Assigns an inherited role to an existing role, with circular dependency check.

        Args:
            role_id (str): The id of the role to update.
            inherited_role_name_to_add (str): The name of the role to inherit.

        Returns:
            RoleReadSchema: The updated role.

        Raises:
            HTTPException: If roles are not found, a circular dependency is detected, or the inherited role is the same as the main role.
        """
        try:
            main_role = await self.role_repos.find_by_id(id=role_id)
            if not main_role:
                raise HTTPException(
                    status_code=404, detail=f"Role '{role_id}' not found."
                )

            inherited_role = await self.role_repos.find_by_name(
                name=inherited_role_name_to_add
            )
            if not inherited_role:
                raise HTTPException(
                    status_code=400,
                    detail=f"Inherited role '{inherited_role_name_to_add}' not found.",
                )

            if main_role.name == inherited_role_name_to_add:
                raise HTTPException(
                    status_code=400,
                    detail="A role cannot inherit itself.",
                )

            # Circular dependency check
            # We need to traverse the graph starting from the inherited_role
            # to see if it eventually inherits the main_role.
            if await self._check_circular_inheritance(
                start_role_name=inherited_role_name_to_add,
                target_role_name=main_role.name,
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"Circular inheritance detected: '{main_role.name}' cannot inherit '{inherited_role_name_to_add}' as it would create a loop.",
                )

            current_inherited_roles = set(main_role.inherited_roles)
            if inherited_role_name_to_add in current_inherited_roles:
                # Already inherited, no change needed, just return current state
                return RoleReadSchema.model_validate(main_role)

            current_inherited_roles.add(inherited_role_name_to_add)

            update_data = {"inherited_roles": list(current_inherited_roles)}
            updated = await self.role_repos.update(
                id=str(main_role.id), update_data=update_data
            )

            if not updated:
                raise HTTPException(
                    status_code=500, detail="Failed to update role inherited roles."
                )

            # Fetch and return the updated role
            updated_role_model = await self.role_repos.find_by_id(id=str(main_role.id))
            if not updated_role_model:
                raise HTTPException(
                    status_code=500, detail="Updated role not found after update."
                )

            return RoleReadSchema.model_validate(updated_role_model)

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while adding inherited role: {str(e)}",
            )

    async def remove_permissions_from_role(
        self, role_id: str, permissions_to_remove: List[str]
    ) -> RoleReadSchema:
        """
        Removes specified permissions from an existing role.

        Args:
            role_id (str): The ID of the role to update.
            permissions_to_remove (List[str]): A list of permission codes to remove.

        Returns:
            RoleReadSchema: The updated role.

        Raises:
            HTTPException: If the role is not found.
        """
        try:
            role = await self.role_repos.find_by_id(id=role_id)
            if not role:
                raise HTTPException(
                    status_code=404, detail=f"Role with ID '{role_id}' not found."
                )

            current_permissions = set(role.permissions)
            # Remove permissions. set.difference() is safe if permission not present.
            current_permissions = current_permissions.difference(permissions_to_remove)

            update_data = {"permissions": list(current_permissions)}
            updated = await self.role_repos.update(
                id=str(role.id), update_data=update_data
            )

            if not updated:
                raise HTTPException(
                    status_code=500, detail="Failed to remove role permissions."
                )

            updated_role_model = await self.role_repos.find_by_id(id=str(role.id))
            if not updated_role_model:
                raise HTTPException(
                    status_code=500, detail="Updated role not found after removal."
                )

            return RoleReadSchema.model_validate(updated_role_model)

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while removing permissions: {str(e)}",
            )

    async def remove_inherited_role(
        self, role_id: str, inherited_role_to_remove_name: str
    ) -> RoleReadSchema:
        """
        Removes an inherited role from an existing role.

        Args:
            role_id (str): The ID of the role to update.
            inherited_role_name_to_remove (str): The name of the inherited role to remove.

        Returns:
            RoleReadSchema: The updated role.

        Raises:
            HTTPException: If the role is not found.
        """
        try:
            main_role = await self.role_repos.find_by_id(id=role_id)
            if not main_role:
                raise HTTPException(
                    status_code=404, detail=f"Role with ID '{role_id}' not found."
                )

            current_inherited_roles = set(main_role.inherited_roles)
            if inherited_role_to_remove_name not in current_inherited_roles:
                # If it's not currently inherited, no change needed, just return current state
                return RoleReadSchema.model_validate(main_role)

            current_inherited_roles.remove(inherited_role_to_remove_name)

            update_data = {"inherited_roles": list(current_inherited_roles)}
            updated = await self.role_repos.update(
                id=str(main_role.id), update_data=update_data
            )

            if not updated:
                raise HTTPException(
                    status_code=500, detail="Failed to remove inherited role."
                )

            updated_role_model = await self.role_repos.find_by_id(id=str(main_role.id))
            if not updated_role_model:
                raise HTTPException(
                    status_code=500, detail="Updated role not found after removal."
                )

            return RoleReadSchema.model_validate(updated_role_model)

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while removing inherited role: {str(e)}",
            )

    async def _check_circular_inheritance(
        self, start_role_name: str, target_role_name: str
    ) -> bool:
        """
        Helper function to check for circular inheritance.
        Performs a BFS-like traversal to see if target_role_name is reachable from start_role_name.
        """
        visited: Set[str] = set()
        queue: List[str] = [start_role_name]

        while queue:
            current_role_name = queue.pop(0)  # Use pop(0) for BFS
            if current_role_name == target_role_name:
                return True  # Circular dependency detected

            if current_role_name in visited:
                continue
            visited.add(current_role_name)

            current_role = await self.role_repos.find_by_name(name=current_role_name)
            if current_role and current_role.inherited_roles:
                for inherited_from_current in current_role.inherited_roles:
                    if inherited_from_current not in visited:
                        queue.append(inherited_from_current)
        return False  # No circular dependency

    """async def _check_circular_inheritance(
        self, start_role_name: str, target_role_name: str
    ) -> bool:
        """


"""      Helper function to check for circular inheritance.
        Performs a DFS-like traversal to see if target_role_name is reachable from start_role_name.
        """
"""    visited: Set[str] = set()
        queue: List[str] = [start_role_name]

        while queue:
            current_role_name = queue.pop(
                0
            )  # Use pop(0) for BFS, or pop() for DFS (less memory for recursion)
            if current_role_name == target_role_name:
                return True  # Circular dependency detected

            if current_role_name in visited:
                continue
            visited.add(current_role_name)

            current_role = await self.role_repos.find_by_name(name=current_role_name)
            if current_role and current_role.inherited_roles:
                for inherited_from_current in current_role.inherited_roles:
                    if inherited_from_current not in visited:
                        queue.append(inherited_from_current)
        return False  # No circular dependency"""
