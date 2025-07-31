from typing import Optional, List
from app.core.security import SecurityUtils
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository
from app.models.User import UserModel
from app.schemas.user import UserCreateSchema, UserUpdateSchema, UserReadSchema
from fastapi import HTTPException


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        role_repos: RoleRepository,
        permission_repos: PermissionRepository,
    ):
        self.user_repo = user_repo
        self.role_repos = role_repos
        self.permission_repos = permission_repos

    async def get_user(self, user_id: str) -> Optional[UserReadSchema]:
        user = await self.user_repo.find_by_id(user_id)
        if user:
            return UserReadSchema.model_validate(user)
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserReadSchema]:
        user = await self.user_repo.find_by_email(email)
        if user:
            return UserReadSchema.model_validate(user)
        return None

    async def list_users(
        self, skip: int = 0, limit: int = 100, all: bool = False
    ) -> List[UserReadSchema]:
        users = await self.user_repo.list_users(skip=skip, limit=limit, all=all)
        return [UserReadSchema.model_validate(u) for u in users]

    async def create_user(self, user_create: UserCreateSchema) -> UserReadSchema:
        existing = await self.user_repo.find_by_email(user_create.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        if user_create.roles:
            db_role_names = {r.name for r in await self.role_repos.list_roles()}
            for role_name in user_create.roles:
                if role_name not in db_role_names:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Role '{role_name}' not found. Please create it first.",
                    )
        if user_create.permissions:
            db_permission_codes = {
                p.code for p in await self.permission_repos.list_permissions()
            }
            for permission_code in user_create.permissions:
                if permission_code not in db_permission_codes:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Permission '{permission_code}' not found. Please create it first.",
                    )

        hashed_pw = SecurityUtils.hash_password(user_create.password)
        user_model = UserModel(
            **user_create.model_dump(exclude=["password"]), password=hashed_pw
        )
        user_id = await self.user_repo.create(user_model)
        created = await self.user_repo.find_by_id(user_id)
        return UserReadSchema.model_validate(created)

    async def update_user(
        self, user_id: str, user_update: UserUpdateSchema
    ) -> UserReadSchema:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user_update.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing = await self.user_repo.find_by_email(update_data["email"])
            if existing and str(existing.id) != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")

        if user_update.roles:
            db_role_names = {r.name for r in await self.role_repos.list_roles()}
            for role_name in user_update.roles:
                if role_name not in db_role_names:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Role '{role_name}' not found. Please create it first.",
                    )
        if user_update.permissions:
            db_permission_codes = {
                p.code for p in await self.permission_repos.list_permissions()
            }
            for permission_code in user_update.permissions:
                if permission_code not in db_permission_codes:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Permission '{permission_code}' not found. Please create it first.",
                    )

        if "password" in update_data:
            update_data["password"] = SecurityUtils.hash_password(
                update_data.pop("password")
            )

        success = await self.user_repo.update(user_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Update failed")

        updated = await self.user_repo.find_by_id(user_id)
        return UserReadSchema.model_validate(updated)

    async def verify_user(self, user_id: str) -> UserReadSchema:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = {"is_verified": True, "is_active": True}

        success = await self.user_repo.update(user_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="User verification failed")

        updated = await self.user_repo.find_by_id(user_id)
        return UserReadSchema.model_validate(updated)

    async def delete_user(self, user_id: str) -> None:
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        success = await self.user_repo.delete(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Delete failed")
        return success

    async def assign_permissions_to_user(
        self, user_id: str, permissions_to_add: List[str]
    ) -> UserReadSchema:
        """
        Assigns new permissions to a user.

        Args:
            role_id (str): The id of the role to update.
            permissions_to_add (List[str]): A list of permission codes to add.

        Returns:
            UserReadSchema: The updated user.

        Raises:
            HTTPException: If the user is not found or any permission is invalid.
        """
        try:
            user = await self.user_repo.find_by_id(user_id=user_id)
            if not user:
                raise HTTPException(
                    status_code=404, detail=f"User '{user_id}' not found."
                )

            # Validate if all permissions to add actually exist
            existing_permissions = await self.permission_repos.find_many_by_codes(
                codes=permissions_to_add
            )
            existing_permission_codes = {p.code for p in existing_permissions}

            for perm_code in permissions_to_add:
                if perm_code not in existing_permission_codes:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Permission '{perm_code}' not found. Please create it first.",
                    )

            # Convert current permissions to a set to easily add new ones and remove duplicates
            current_permissions = set(user.permissions)
            current_permissions.update(permissions_to_add)

            update_data = {"permissions": list(current_permissions)}
            updated = await self.user_repo.update(
                user_id=str(user.id), update_data=update_data
            )

            if not updated:
                raise HTTPException(
                    status_code=500, detail="Failed to update user permissions."
                )

            # Fetch and return the updated role
            updated_user_model = await self.user_repo.find_by_id(user_id=str(user.id))
            if not updated_user_model:
                raise HTTPException(
                    status_code=500, detail="Updated user not found after update."
                )

            return UserReadSchema.model_validate(updated_user_model)

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while assigning permissions: {str(e)}",
            )

    async def assign_roles_to_user(
        self, user_id: str, roles_to_add: List[str]
    ) -> UserReadSchema:
        """
        Assigns new roles to a user.

        Args:
            role_id (str): The id of the role to update.
            roles_to_add (List[str]): A list of roles names to add.

        Returns:
            UserReadSchema: The updated user.

        Raises:
            HTTPException: If the user is not found or any role is invalid.
        """
        try:
            user = await self.user_repo.find_by_id(user_id=user_id)
            if not user:
                raise HTTPException(
                    status_code=404, detail=f"User '{user_id}' not found."
                )

            # Validate if all roles to add actually exist
            existing_roles = await self.role_repos.find_many_by_names(
                names=roles_to_add
            )
            existing_role_names = {r.name for r in existing_roles}

            for role_name in roles_to_add:
                if role_name not in existing_role_names:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Role '{role_name}' not found. Please create it first.",
                    )

            # Convert current roles to a set to easily add new ones and remove duplicates
            current_roles = set(user.roles)
            current_roles.update(roles_to_add)

            update_data = {"roles": list(current_roles)}
            updated = await self.user_repo.update(
                user_id=str(user.id), update_data=update_data
            )

            if not updated:
                raise HTTPException(
                    status_code=500, detail="Failed to update user roles."
                )

            # Fetch and return the updated role
            updated_user_model = await self.user_repo.find_by_id(user_id=str(user.id))
            if not updated_user_model:
                raise HTTPException(
                    status_code=500, detail="Updated user not found after update."
                )

            return UserReadSchema.model_validate(updated_user_model)

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while assigning roles: {str(e)}",
            )

    async def remove_permissions_from_user(
        self, user_id: str, permissions_to_remove: List[str]
    ) -> UserReadSchema:
        """
        Removes specified permissions from a user.

        Args:
            user_id (str): The ID of the user to update.
            permissions_to_remove (List[str]): A list of permission codes to remove.

        Returns:
            UserReadSchema: The updated role.

        Raises:
            HTTPException: If the user is not found.
        """
        try:
            user = await self.user_repo.find_by_id(user_id=user_id)
            if not user:
                raise HTTPException(
                    status_code=404, detail=f"User with ID '{user_id}' not found."
                )

            current_permissions = set(user.permissions)
            current_permissions = current_permissions.difference(permissions_to_remove)

            update_data = {"permissions": list(current_permissions)}
            updated = await self.user_repo.update(
                user_id=user.id, update_data=update_data
            )

            if not updated:
                raise HTTPException(
                    status_code=500, detail="Failed to remove user permissions."
                )

            updated_user_model = await self.user_repo.find_by_id(user_id=str(user.id))
            if not updated_user_model:
                raise HTTPException(
                    status_code=500, detail="Updated user not found after removal."
                )

            return UserReadSchema.model_validate(updated_user_model)

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while removing permissions: {str(e)}",
            )

    async def remove_roles_from_user(
        self, user_id: str, roles_to_remove: List[str]
    ) -> UserReadSchema:
        """
        Removes specified roles from a user.

        Args:
            role_id (str): The ID of the user to update.
            roles_to_remove (List[str]): A list of roles names to remove.

        Returns:
            UserReadSchema: The updated role.

        Raises:
            HTTPException: If the user is not found.
        """
        try:
            user = await self.user_repo.find_by_id(user_id=user_id)
            if not user:
                raise HTTPException(
                    status_code=404, detail=f"User with ID '{user_id}' not found."
                )

            current_roles = set(user.roles)
            current_roles = current_roles.difference(roles_to_remove)

            update_data = {"roles": list(current_roles)}
            updated = await self.user_repo.update(
                user_id=user.id, update_data=update_data
            )

            if not updated:
                raise HTTPException(
                    status_code=500, detail="Failed to remove user roles."
                )

            updated_user_model = await self.user_repo.find_by_id(user_id=str(user.id))
            if not updated_user_model:
                raise HTTPException(
                    status_code=500, detail="Updated user not found after removal."
                )

            return UserReadSchema.model_validate(updated_user_model)

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while removing roles: {str(e)}",
            )
