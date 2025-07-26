from pydantic import ConfigDict, EmailStr, Field
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = Field(..., alias="ENV")

    # fallback généraux
    default_db_uri: str = Field(
        ..., json_schema_extra={"env": "DATABASE_URI"}, alias="DATABASE_URI"
    )
    default_db_name: str = Field(..., alias="DB_NAME")

    # Paramètres JWT et de token
    jwt_algorithm: str = Field(..., alias="JWT_ALGORITHM")
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    access_token_expire_weeks: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_WEEKS")

    # Paramètre du superadministrateur
    admin_email: str = Field(..., alias="ADMINEMAIL")
    admin_password: str = Field(..., alias="ADMINPASSWORD")

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        validate_by_name=True,
        extra="allow",
        frozen=True,
    )

    # Paramètres OTP
    otp_expiry_minutes: int = Field(..., alias="OTP_EXPIRY_MINUTES")
    otp_length: int = Field(..., alias="OTP_LENGTH")

    # Paramètres d'envoi d'e-mail (SMTP)
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_username: str = "your_email@example.com"
    smtp_password: str = "your_email_password"
    smtp_sender_email: EmailStr = "noreply@example.com"
    smtp_use_tls: bool = True
    # smtp_use_ssl: bool = False            # Utiliser SSL (pour le port 465)

    # Paramètre de la base de données en fonction de l'environnement
    @property
    def database_uri(self) -> str:
        return (
            os.getenv(f"DATABASE_URI_{self.environment.upper()}") or self.default_db_uri
        )

    @property
    def database_name(self) -> str:
        return os.getenv(f"DB_NAME_{self.environment.upper()}") or self.default_db_name
