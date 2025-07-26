from pydantic import ConfigDict, EmailStr, Field
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Base class of all app settings and configuration params

    Args:
        BaseSettings (_type_): _description_

    Returns:
        Settings: with all env and config properties
    """

    environment: str = Field(..., alias="ENV")
    app_name: str = Field(..., alias="APP_NAME")
    base_url: str = Field(..., alias="BASE_URL")

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

    # Paramètres OTP
    otp_expiry_minutes: int = Field(..., alias="OTP_EXPIRY_MINUTES")
    otp_length: int = Field(..., alias="OTP_LENGTH")

    # Paramètres d'envoi d'e-mail (SMTP)
    smtp_host: str = Field(..., alias="SMTP_HOST")
    smtp_port: int = Field(..., alias="SMTP_PORT")
    smtp_username: str = Field(..., alias="SMTP_USERNAME")
    smtp_password: str = Field(..., alias="SMTP_PASSWORD")
    smtp_sender_email: EmailStr = Field(..., alias="SMTP_SENDER_EMAIL")
    smtp_use_tls: bool = Field(..., alias="SMTP_USE_TLS")
    smtp_use_ssl: bool = False  # Utiliser SSL (pour le port 465)

    # Paramètres Google OAuth
    google_oauth_client_id: str = Field(..., alias="GOOGLE_OAUTH_CLIENT_ID")
    google_oauth_client_secret: str = Field(..., alias="GOOGLE_OAUTH_CLIENT_SECRET")
    google_oauth_redirect_uri: str = Field(..., alias="GOOGLE_OAUTH_REDIRECT_URI")

    # Chemin des templates
    templates_dir: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates"
    )

    # Paramètre de la base de données en fonction de l'environnement
    @property
    def database_uri(self) -> str:
        return (
            os.getenv(f"DATABASE_URI_{self.environment.upper()}") or self.default_db_uri
        )

    @property
    def database_name(self) -> str:
        return os.getenv(f"DB_NAME_{self.environment.upper()}") or self.default_db_name

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        validate_by_name=True,
        extra="allow",
        frozen=True,
    )
