from pydantic import BaseSettings, Field
from functools import lru_cache
import os


class Settings(BaseSettings):
    environment: str = Field(..., env="ENV")

    # fallback généraux
    default_db_uri: str = Field(..., env="DATABASE_URI")
    default_db_name: str = Field(..., env="DB_NAME")

    jwt_algorithm: str = Field(..., env="JWT_SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    access_token_expire_weeks: int = Field(..., env="ACCESS_TOKEN_EXPIRE_WEEKS")

    admin_email: str = Field(..., env="ADMINEMAIL")
    admin_password: str = Field(..., env="ADMINPASSWORD")

    class Config:
        case_sensitive = True

    @property
    def database_uri(self) -> str:
        return (
            os.getenv(f"DATABASE_URI_{self.environment.upper()}") or self.default_db_uri
        )

    @property
    def database_name(self) -> str:
        return os.getenv(f"DB_NAME_{self.environment.upper()}") or self.default_db_name
