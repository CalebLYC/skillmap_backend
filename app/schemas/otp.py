import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional

from app.models.OTP import OTPTypeEnum
from app.schemas.user import UserReadSchema


class OTPRequestSchema(BaseModel):
    """
    Schéma pour la requête de génération d'un OTP.
    """

    email: EmailStr = Field(
        ..., description="L'adresse e-mail pour laquelle un OTP est demandé."
    )
    type: Optional[OTPTypeEnum] = Field(
        description="Le type du code OTP généré.",
        default=OTPTypeEnum.VERIFY_USER,
    )
    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "type": "verify_user",
            }
        },
    )


class OTPVerifySchema(BaseModel):
    """
    Schéma pour la vérification d'un OTP.
    """

    email: EmailStr = Field(..., description="L'adresse e-mail associée à l'OTP.")
    code: str = Field(
        ..., min_length=4, max_length=8, description="Le code OTP à vérifier."
    )
    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "code": "838162",
            }
        },
    )


class OTPResponseSchema(BaseModel):
    """
    Schéma de réponse pour les opérations OTP.
    """

    detail: Optional[str] = Field(
        default=None, description="Message de statut de l'opération OTP."
    )
    otp_id: Optional[str] = Field(
        None, description="L'ID de l'OTP généré (si applicable)."
    )
    email: EmailStr = Field(
        ..., description="L'adresse e-mail à laquelle l'OTP est envoyé."
    )
    # code: str = Field(..., description="Le code OTP généré.")
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
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "detail": "OTP sent successfully to jdoe@example.com. It will expire in 5 minutes.",
                "otp_id": "68839b57869a2157af64cf73",
                "email": "jdoe@example.com",
                "code": "838162",
                "expires_at": "2025-07-25T15:02:27.685000",
                "is_used": False,
                "created_at": "2025-07-25T14:57:27.685000",
                "type": "verify_user",
            }
        },
    )


class OTPVerifyResponseSchema(BaseModel):
    """
    Schéma de réponse pour les opérations OTP.
    """

    detail: str = Field(..., description="Message de statut de l'opération OTP.")
    otp: Optional[OTPResponseSchema] = Field(
        default=None, description="Le model de l'OTP généré."
    )
    user: Optional[UserReadSchema] = Field(
        default=None, description="L'utilisateur vérifié."
    )
