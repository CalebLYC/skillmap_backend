import datetime

from jose import JWTError, jwt
from app.providers.providers import get_settings


class JWTUtils:
    _instance = None
    _settings = None

    def __new__(cls):
        if cls._instance == None:
            cls._instance = super(JWTUtils, cls).__new__(cls)
            cls._settings = get_settings()
        return cls._instance

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: datetime.timedelta = None
    ) -> tuple[str, datetime.datetime]:
        # S'assurer que le singleton est instancié
        if JWTUtils._settings is None:
            JWTUtils()
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.timezone.utc) + (
            expires_delta
            if expires_delta
            else datetime.timedelta(
                (JWTUtils._settings.access_token_expire_weeks) * 10080
            )
        )
        to_encode.update({"exp": expire})
        return (
            jwt.encode(
                to_encode,
                JWTUtils._settings.jwt_secret_key,
                algorithm=JWTUtils._settings.jwt_algorithm,
            ),
            expire,
        )

    @staticmethod
    def decode_access_token(token: str) -> dict:
        # S'assurer que le singleton est instancié
        if JWTUtils._settings is None:
            JWTUtils()
        try:
            payload = jwt.decode(
                token,
                JWTUtils._settings.jwt_secret_key,
                algorithms=[JWTUtils._settings.jwt_algorithm],
            )
            return payload
        except:
            return None
