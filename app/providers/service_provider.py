from fastapi import Depends
from app.core.config import Settings
from app.db.repositories.access_token_repository import AccessTokenRepository
from app.db.repositories.otp_repository import OTPRepository
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository
from app.providers.providers import get_settings
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
from app.services.email_service import EmailService


def get_email_service(
    settings: Settings = Depends(get_settings),
) -> EmailService:
    """Provides email service

    Args:
        settings (Settings, optional): _description_. Defaults to Depends(get_settings).

    Returns:
        EmailService: _description_
    """
    return EmailService(settings=settings)


def get_auth_service(
    user_repos: UserRepository = Depends(get_user_repository),
    access_token_repos: AccessTokenRepository = Depends(get_access_token_repository),
    otp_repos: OTPRepository = Depends(get_otp_repository),
) -> AuthService:
    """Provides auth service

    Args:
        user_repos (UserRepository, optional): _description_. Defaults to Depends(get_user_repository).
        access_token_repos (AccessTokenRepository, optional): _description_. Defaults to Depends(get_access_token_repository).
        otp_repos (OTPRepository, optional): _description_. Defaults to Depends(get_otp_repository).

    Returns:
        AuthService: _description_
    """
    return AuthService(
        user_repos=user_repos,
        access_token_repos=access_token_repos,
        otp_repos=otp_repos,
    )


def get_user_service(
    user_repos: UserRepository = Depends(get_user_repository),
    role_repos: RoleRepository = Depends(get_role_repository),
    permission_repos: PermissionRepository = Depends(get_permission_repository),
) -> UserService:
    """Provides user service

    Args:
        user_repos (UserRepository, optional): _description_. Defaults to Depends(get_user_repository).
        role_repos (RoleRepository, optional): _description_. Defaults to Depends(get_role_repository).
        permission_repos (PermissionRepository, optional): _description_. Defaults to Depends(get_permission_repository).

    Returns:
        UserService: _description_
    """
    return UserService(
        user_repo=user_repos, role_repos=role_repos, permission_repos=permission_repos
    )


def get_permission_service(
    role_repos: RoleRepository = Depends(get_role_repository),
    permission_repos: PermissionRepository = Depends(get_permission_repository),
) -> PermissionService:
    """Provides permission service

    Args:
        role_repos (RoleRepository, optional): _description_. Defaults to Depends(get_role_repository).
        permission_repos (PermissionRepository, optional): _description_. Defaults to Depends(get_permission_repository).

    Returns:
        PermissionService: _description_
    """
    return PermissionService(role_repos=role_repos, permission_repos=permission_repos)


def get_role_service(
    role_repos: RoleRepository = Depends(get_role_repository),
    permission_repos: PermissionRepository = Depends(get_permission_repository),
) -> RoleService:
    """Provides role service

    Args:
        role_repos (RoleRepository, optional): _description_. Defaults to Depends(get_role_repository).
        permission_repos (PermissionRepository, optional): _description_. Defaults to Depends(get_permission_repository).

    Returns:
        RoleService: _description_
    """
    return RoleService(role_repos=role_repos, permission_repos=permission_repos)


def get_otp_service(
    user_repos: UserRepository = Depends(get_user_repository),
    otp_repos: OTPRepository = Depends(get_otp_repository),
    email_service: EmailService = Depends(get_email_service),
    settings: Settings = Depends(get_settings),
) -> UserService:
    """Provides OTP service

    Args:
        user_repos (UserRepository, optional): _description_. Defaults to Depends(get_user_repository).
        otp_repos (OTPRepository, optional): _description_. Defaults to Depends(get_otp_repository).
        settings (Settings, optional): _description_. Defaults to Depends(get_settings).

    Returns:
        UserService: _description_
    """
    return OTPService(
        otp_repos=otp_repos,
        user_repos=user_repos,
        settings=settings,
        email_service=email_service,
    )
