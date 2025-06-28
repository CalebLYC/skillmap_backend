from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class UserCreateSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    full_name: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "name": "Doe",
                "firstname": "John",
                "password": "12345678",
            }
        },
    )


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


class UserReadSchema(BaseModel):
    id: str = Field(..., alias="_id", serialization_alias="id")
    email: EmailStr = Field(...)
    full_name: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "email": "jdoe@example.com",
                "name": "Doe",
                "firstname": "John",
                "password": "12345678",
            }
        },
    )
