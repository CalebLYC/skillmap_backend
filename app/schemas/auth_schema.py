import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.AccessToken import AccessTokenModel
from app.models.User import SexEnum
from app.schemas.user import UserReadSchema


class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str
    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "password": "12345678",
            }
        },
    )


class LoginResponseSchema(BaseModel):
    user: UserReadSchema
    access_token: AccessTokenModel
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={ObjectId: str},
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class RegisterSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    password_confirmation: Optional[str] = Field(default=None)
    first_name: str = Field(...)
    last_name: str = Field(...)
    phone_number: Optional[str] = Field(default=None)
    sex: Optional[SexEnum] = Field(default=None)
    birthday_date: Optional[datetime.datetime] = Field(default=None)

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "email*": "jdoe@example.com",
                "last_name*": "Doe",
                "first_name*": "John",
                "password*": "12345678",
                "password_confirmation": "12345678",
                "phone_number": "90000000",
                "sex": "M",
                "birthday_date": "2004-01-01",
            }
        },
    )


class ResetUserPasswordSchema(BaseModel):
    """
    Schéma pour reset un mot de passe oublié.
    """

    email: EmailStr = Field(..., description="L'adresse e-mail associée à l'OTP.")
    code: str = Field(
        ..., min_length=4, max_length=8, description="Le code OTP à vérifier."
    )
    new_password: Optional[str] = Field(
        description="Le nouveau mot de passe.",
        default=None,
    )
    new_password_confirmation: Optional[str] = Field(
        description="La confirmation du nouveau mot de passe.",
        default=None,
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
                "new_password": "12345678",
                "new_password_confirmation": "12345678",
            }
        },
    )


class ChangeUserPasswordSchema(BaseModel):
    """
    Schéma pour changer un mot de passe.
    """

    old_password: str = Field(
        ...,
        description="L'ancien mot de passe.",
    )
    new_password: str = Field(
        ...,
        description="Le nouveau mot de passe.",
    )
    new_password_confirmation: Optional[str] = Field(
        description="La confirmation du nouveau mot de passe.",
        default=None,
    )
    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "new_password": "12345678",
                "new_password_confirmation": "12345678",
            }
        },
    )
