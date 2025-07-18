from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.jwt import JWTUtils
from app.providers.repository_provider import (
    get_access_token_repository,
    get_user_repository,
)
from app.providers.service_provider import get_permission_service, get_role_service
from app.db.repositories.access_token_repository import AccessTokenRepository
from app.db.repositories.user_repository import UserRepository
from app.models.User import UserModel
from app.schemas.user import UserReadSchema
from app.services.auth.permission_service import PermissionService
from app.services.auth.role_service import RoleService


oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_token(
    token: str = Depends(oauth_2_scheme),
    access_token_repos: AccessTokenRepository = Depends(get_access_token_repository),
) -> str:
    try:
        payload = JWTUtils.decode_access_token(token=token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        access_token = await access_token_repos.find_by_token_and_user_id(
            user_id=user_id, token=token
        )
        if not access_token:
            raise HTTPException(status_code=401, detail="Expired")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def auth_middleware(
    user_id: str = Depends(verify_token),
    user_repos: UserRepository = Depends(get_user_repository),
) -> UserModel:
    try:
        # print(user_id)
        user = await user_repos.find_by_id(user_id=user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user by token: {str(e)}",
        )


def require_permission(permission_code: str):
    try:

        async def dependency(
            user: UserModel = Depends(auth_middleware),
            ps: PermissionService = Depends(get_permission_service),
        ):
            try:
                await ps.ensure_permission(
                    user=UserReadSchema.model_validate(user),
                    permission_code=permission_code,
                )
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error ensuring permission: {str(e)}",
                )

        return Depends(dependency)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while setting permission dependency: {str(e)}",
        )


def require_role(role_name: str):
    try:

        async def dependency(
            user: UserModel = Depends(auth_middleware),
            rs: RoleService = Depends(get_role_service),
        ):
            try:
                await rs.ensure_role(
                    user=UserReadSchema.model_validate(user), role_name=role_name
                )
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error ensuring role: {str(e)}",
                )

        return Depends(dependency)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while setting permission dependency: {str(e)}",
        )
