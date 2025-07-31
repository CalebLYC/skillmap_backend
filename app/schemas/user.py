import datetime
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional

from app.models.User import SexEnum


class UserCreateSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    phone_number: Optional[str] = Field(default=None)
    sex: Optional[SexEnum] = Field(default=None)
    birthday_date: Optional[datetime.datetime] = Field(default=None)
    roles: Optional[List[str]] = Field(default=[])
    permissions: Optional[List[str]] = Field(default=[])
    picture: Optional[str] = Field(default=None)
    social_login__id: Optional[str] = Field(default=None)
    social_login_provider: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email*": "jdoe@example.com",
                "last_name*": "Doe",
                "first_name*": "John",
                "password*": "12345678",
                "phone_number": "90000000",
                "sex": "M",
                "birthday_date": "2004-01-01",
                "roles": ["user"],
                "permissions": ["user:read"],
                "picture": "https://example.com/picture.jpg",
                "social_login__id": "google_id_12345",
                "social_login_provider": "google",
                "locale": "en-US",
            }
        },
    )


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    sex: Optional[SexEnum] = Field(default=None)
    birthday_date: Optional[datetime.datetime] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    is_verified: Optional[bool] = Field(default=None)
    roles: Optional[List[str]] = Field(default=None)
    permissions: Optional[List[str]] = Field(default=None)
    picture: Optional[str] = Field(default=None)
    # social_login__id: Optional[str] = Field(default=None)
    # social_login_provider: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "last_name": "Doe",
                "first_name": "John",
                "password": "12345678",
                "phone_number": "90000000",
                "sex": "M|F",
                "birthday_date": "2004-01-01",
                "roles": ["user"],
                "permissions": ["user:read"],
                "is_active": True,
                "is_verified": True,
                "picture": "https://example.com/picture.jpg",
                # "social_login__id": "google_id_12345",
                # "social_login_provider": "google",
                "locale": "en-US",
            }
        },
    )


class UserReadSchema(BaseModel):
    id: str = Field(..., alias="_id", serialization_alias="id")
    email: EmailStr = Field(...)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    sex: Optional[SexEnum] = Field(default=None)
    birthday_date: Optional[datetime.datetime] = Field(default=None)
    created_at: Optional[datetime.datetime] = Field(default=None)
    roles: List[str] = Field(default=[])
    permissions: List[str] = Field(default=[])
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    picture: Optional[str] = Field(default=None)
    social_login__id: Optional[str] = Field(default=None)
    social_login_provider: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "id": "685f420bf748b6ad4f8317b5",
                "email": "jdoe@example.com",
                "last_name": "Doe",
                "first_name": "John",
                "password": "12345678",
                "phone_number": "90000000",
                "sex": "M|F",
                "roles": ["user"],
                "permissions": ["user:read"],
                "birthday_date": "2004-01-01",
                "created_at": "20025-01-01",
                "is_active": True,
                "is_verified": True,
                "picture": "https://example.com/picture.jpg",
                "social_login__id": "google_id_12345",
                "social_login_provider": "google",
                "locale": "en-US",
            }
        },
    )
