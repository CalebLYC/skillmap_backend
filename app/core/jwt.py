from datetime import datetime, timedelta

from jose import JWTError, jwt
from app.core.providers import get_settings


class JWTUtils:
    _instance = None
    _settings = None

    def __new__(cls):
        if cls._instance == None:
            cls._instance = super(JWTUtils, cls).__new__(cls)
            cls._settings = get_settings()
        return cls._instance

    def create_access_token(data: dict, expires_delta: timedelta = None):
        # S'assurer que le singleton est instancié
        if JWTUtils._settings is None:
            JWTUtils()
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta or timedelta(
            (JWTUtils._settings.access_token_expire_weeks) * 10080
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            JWTUtils._settings.jwt_secret_key,
            algorithm=JWTUtils._settings.jwt_algorithm,
        )

    def decode_access_token(token: str):
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
