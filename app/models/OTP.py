import datetime
from enum import Enum
from typing_extensions import Annotated
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field


PyObjectId = Annotated[str, BeforeValidator(str)]


class OTPTypeEnum(str, Enum):
    VERIFY_USER = "verify_user"
    RESET_PASSWORD = "password_reset"


class OTPModel(BaseModel):
    """
    Modèle de données pour un One-Time Password (OTP) stocké en base de données.
    """

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr = Field(
        ..., description="L'adresse e-mail à laquelle l'OTP est envoyé."
    )
    code: str = Field(..., description="Le code OTP généré.")
    expires_at: datetime.datetime = Field(
        ..., description="Date et heure d'expiration de l'OTP."
    )
    is_used: bool = Field(
        default=False, description="Indique si l'OTP a déjà été utilisé."
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Date et heure de création de l'OTP.",
    )
    type: OTPTypeEnum = Field(
        description="Le type du code OTP généré.",
        default=OTPTypeEnum.VERIFY_USER,
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={PyObjectId: str},
        arbitrary_types_allowed=True,
    )

    def is_expired(self) -> bool:
        """Vérifie si l'OTP a expiré."""
        if self.expires_at.tzinfo is None:
            self.expires_at = self.expires_at.replace(tzinfo=datetime.timezone.utc)
        return datetime.datetime.now(datetime.timezone.utc) > self.expires_at

    def is_valid(self) -> bool:
        """Vérifie si l'OTP est valide (non expiré et non utilisé)."""
        return not self.is_expired() and not self.is_used
