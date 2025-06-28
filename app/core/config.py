from pydantic import ConfigDict, Field
from functools import lru_cache
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = Field(..., alias="ENV")

    # fallback généraux
    default_db_uri: str = Field(
        ..., json_schema_extra={"env": "DATABASE_URI"}, alias="DATABASE_URI"
    )
    default_db_name: str = Field(..., alias="DB_NAME")

    jwt_algorithm: str = Field(..., alias="JWT_ALGORITHM")
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    access_token_expire_weeks: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_WEEKS")

    admin_email: str = Field(..., alias="ADMINEMAIL")
    admin_password: str = Field(..., alias="ADMINPASSWORD")

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        validate_by_name=True,
        extra="allow",
    )

    @property
    def database_uri(self) -> str:
        return (
            os.getenv(f"DATABASE_URI_{self.environment.upper()}") or self.default_db_uri
        )

    @property
    def database_name(self) -> str:
        return os.getenv(f"DB_NAME_{self.environment.upper()}") or self.default_db_name
