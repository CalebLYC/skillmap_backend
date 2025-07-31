from typing import Any, Dict
from urllib.parse import urlencode
from fastapi import HTTPException, status
import httpx
from app.core.config import Settings


class GoogleAuthService:
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    # Scopes demandés :
    # 'openid' : Indique que l'application utilise OpenID Connect
    # 'email' : Demande l'accès à l'adresse e-mail de l'utilisateur
    # 'profile' : Demande l'accès au profil de base de l'utilisateur (nom, photo)
    GOOGLE_SCOPES = "openid email profile"

    def __init__(self, settings: Settings):
        self.client_id = settings.google_oauth_client_id
        self.client_secret = settings.google_oauth_client_secret
        self.redirect_uri = f"{settings.base_url}{settings.google_oauth_redirect_uri}"
        self.http_client = httpx.AsyncClient()

    def get_authorization_url(self) -> str:
        """Génère l'URL d'autorisation Google OAuth.
        Les utilisateurs seront redirigés vers cette URL pour se connecter à Google.

        Returns:
            str: _description_
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.GOOGLE_SCOPES,
            "access_type": "offline",  # Request offline access for refresh tokens
            "prompt": "select_account",  # Force consent screen to show
        }
        return f"{self.GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def get_tokens_from_code(self, code: str) -> Dict[str, Any]:
        """Échange le code d'autorisation Google contre des jetons d'accès et d'actualisation.

        Args:
            code (str): _description_

        Returns:
            Dict[str, Any]: _description_
        """
        try:
            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
            }
            response = await self.http_client.post(self.GOOGLE_TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur lors de l'échange du code d'autorisation : {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur réseau lors de l'échange du code Google : {str(e)}",
            )

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Récupère les informations de l'utilisateur à partir de l'API Google UserInfo
        en utilisant le jeton d'accès.

        Args:
            access_token (str): _description_

        Returns:
            Dict[str, Any]: _description_
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = await self.http_client.get(
                self.GOOGLE_USERINFO_URL, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erreur lors de la récupération des informations utilisateur Google : {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur réseau lors de la récupération des informations utilisateur Google : {str(e)}",
            )

    async def __aenter__(self):
        """Méthode pour le contexte asynchrone (__aenter__).

        Returns:
            _type_: _description_
        """
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Méthode pour le contexte asynchrone (__aexit__).

        Args:
            exc_type (_type_): _description_
            exc_value (_type_): _description_
            traceback (_type_): _description_
        """
        await self.http_client.aclose()  # Ferme le client HTTP asynchrone lors de la sortie du contexte
