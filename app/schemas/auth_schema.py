import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.access_token import AccessTokenModel
from app.models.user import SexEnum, UserModel
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
                "email": "jdoe@example.com",
                "last_name": "Doe",
                "first_name": "John",
                "password": "12345678",
                "password_confirmation": "12345678",
                "phone_number": "90000000",
                "sex": "M",
                "birthday_date": "2004-01-01",
            }
        },
    )
