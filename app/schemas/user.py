from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class UserCreateSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    phone_number: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "last_name": "Doe",
                "first_name": "John",
                "password": "12345678",
                "phone_number": "90000000",
            }
        },
    )


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    phone_nulber: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "last_name": "Doe",
                "first_name": "John",
                "password": "12345678",
                "phone_number": "90000000",
            }
        },
    )


class UserReadSchema(BaseModel):
    id: str = Field(..., alias="_id", serialization_alias="id")
    email: EmailStr = Field(...)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)

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
            }
        },
    )
