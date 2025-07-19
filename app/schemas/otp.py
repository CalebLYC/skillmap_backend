import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.schemas.user import UserReadSchema


class OTPRequestSchema(BaseModel):
    """
    Schéma pour la requête de génération d'un OTP.
    """

    email: EmailStr = Field(
        ..., description="L'adresse e-mail pour laquelle un OTP est demandé."
    )


class OTPVerifySchema(BaseModel):
    """
    Schéma pour la vérification d'un OTP.
    """

    email: EmailStr = Field(..., description="L'adresse e-mail associée à l'OTP.")
    code: str = Field(
        ..., min_length=4, max_length=8, description="Le code OTP à vérifier."
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
