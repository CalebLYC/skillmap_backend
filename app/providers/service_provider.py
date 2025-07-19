from fastapi import Depends
from app.db.repositories.access_token_repository import AccessTokenRepository
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository
from app.providers.repository_provider import (
    get_access_token_repository,
    get_otp_repository,
    get_permission_repository,
    get_role_repository,
    get_user_repository,
)
from app.services.auth.auth_service import AuthService
from app.services.auth.otp_service import OTPService
from app.services.auth.permission_service import PermissionService
from app.services.auth.role_service import RoleService
from app.services.auth.user_service import UserService


def get_auth_service(
    user_repos: UserRepository = Depends(get_user_repository),
    access_token_repos: AccessTokenRepository = Depends(get_access_token_repository),
) -> AuthService:
    return AuthService(user_repos=user_repos, access_token_repos=access_token_repos)


def get_user_service(
    user_repos: UserRepository = Depends(get_user_repository),
    role_repos: RoleRepository = Depends(get_role_repository),
    permission_repos: PermissionRepository = Depends(get_permission_repository),
) -> UserService:
    return UserService(
        user_repo=user_repos, role_repos=role_repos, permission_repos=permission_repos
    )


def get_permission_service(
    role_repos: RoleRepository = Depends(get_role_repository),
    permission_repos: PermissionRepository = Depends(get_permission_repository),
) -> PermissionService:
    return PermissionService(role_repos=role_repos, permission_repos=permission_repos)


def get_role_service(
    role_repos: RoleRepository = Depends(get_role_repository),
    permission_repos: PermissionRepository = Depends(get_permission_repository),
) -> RoleService:
    return RoleService(role_repos=role_repos, permission_repos=permission_repos)


def get_otp_service(
    user_repos: UserRepository = Depends(get_user_repository),
    otp_repos: RoleRepository = Depends(get_otp_repository),
) -> UserService:
    return OTPService(
        otp_repos=otp_repos,
        user_repos=user_repos,
    )
