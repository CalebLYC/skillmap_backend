# Router
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends, Query
from fastapi.responses import RedirectResponse

from app.core.config import Settings
from app.providers.providers import get_settings
from app.providers.service_provider import (
    get_auth_service,
    get_google_auth_service,
    get_user_service,
)
from app.schemas.auth_schema import LoginResponseSchema
from app.schemas.user_schema import UserCreateSchema, UserUpdateSchema
from app.services.auth.auth_service import AuthService
from app.services.auth.google_auth_service import GoogleAuthService
from app.services.auth.user_service import UserService
from app.utils.constants import http_status


router = APIRouter(
    tags=["Google Auth"],
    dependencies=[],
    responses=http_status.router_responses,
    prefix="/auth/google",
)


@router.get(
    "/login",
    response_class=RedirectResponse,
    summary="Initiate Google OAuth login",
    status_code=status.HTTP_302_FOUND,
)
async def google_login(
    service: GoogleAuthService = Depends(get_google_auth_service),
    client_type: Optional[str] = Query(
        None, description="Type of client (e.g., 'web', 'mobile')"
    ),
):
    """Redirects the user to Google's authorization URL to initiate the OAuth flow.

    Args:
        service (GoogleAuthService, optional): _description_. Defaults to Depends(get_google_auth_service).

    Returns:
        _type_: _description_
    """
    authorization_url = service.get_authorization_url()
    return RedirectResponse(url=authorization_url)


@router.get(
    "/callback",
    summary="Handle Google OAuth callback",
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK,
    response_class=RedirectResponse,
)
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    service: GoogleAuthService = Depends(get_google_auth_service),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
):
    """Handles the callback from Google after the user has authenticated.

    Args:
        code (str): The authorization code returned by Google.
        service (GoogleAuthService, optional): _description_. Defaults to Depends(get_google_auth_service).

    Returns:
        Dict[str, Any]: Contains access and refresh tokens.
    """
    try:
        tokens = await service.get_tokens_from_code(code=code)
        access_token_google = tokens.get("access_token")
        if not access_token_google:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received from Google.",
            )

        user_info = await service.get_user_info(access_token=access_token_google)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User info not provided by google.",
            )
        google_email = user_info.get("email")
        google_first_name = user_info.get("given_name")
        google_last_name = user_info.get("family_name")
        google_picture = user_info.get("picture")
        google_id = user_info.get("sub")
        locale = user_info.get("locale")
        if not google_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No email found in Google user information.",
            )

        user = await user_service.get_user_by_email(email=google_email)
        if not user:
            new_user_data = UserCreateSchema(
                email=google_email,
                first_name=google_first_name,
                last_name=google_last_name,
                password=auth_service.generate_random_password(),
                is_verified=True,
                picture=google_picture,
                social_login__id=google_id,
                social_login_provider="google",
                locale=locale,
            )
            user = await user_service.create_user(user_create=new_user_data)
            print(f"Nouvel utilisateur créé via Google: {user.email}")
        else:
            if not user.is_verified:
                verification_success = await user_service.verify_user(
                    user_id=str(user.id)
                )
                if not verification_success:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User verification failed.",
                    )
                """await user_service.update_user(
                    user_id=str(user.id),
                    user_update=UserUpdateSchema(
                        "social_login__id": google_id,
                        "social_login_provider": "google",
                    )
                )"""
                print(f"Utilisateur existant vérifié via Google: {user.email}")
            if not user.picture:
                await user_service.update_user(
                    user_id=str(user.id),
                    user_update=UserUpdateSchema(picture=google_picture),
                )
                print(
                    f"Photo de profil de l'utilisateur existant ajouté via Google: {user.email}"
                )
            """if not user.locale:
                await user_service.update_user(
                    user_id=str(user.id),
                    user_update=UserUpdateSchema(locale=locale),
                )
                print(
                    f"Locale de l'utilisateur existant mis à jour via Google: {user.email}"
                )"""

            print(f"Utilisateur existant connecté via Google: {user.email}")

        access_token = await auth_service.generate_and_get_access_token(
            user_id=str(user.id)
        )
        """return LoginResponseSchema(
            access_token=access_token,
            # refresh_token=None,  # Refresh token logic can be added later
            user=user,
        )"""
        redirect_url = f"{settings.web_frontend_url}{settings.frontend_auth_success_redirect_uri}#access_token={access_token}&token_type=bearer"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during Google authentication: {str(e)}",
        )
