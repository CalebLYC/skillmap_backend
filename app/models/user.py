import datetime
from enum import Enum
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field
from typing import Annotated, List, Optional
from bson import ObjectId


def validate_object_id(v: str) -> str:
    if not ObjectId.is_valid(v):
        raise ValueError(f"Invalid ObjectId: {v}")
    return v


class SexEnum(str, Enum):
    MALE = "M"
    FEMALE = "F"


PyObjectId = Annotated[str, BeforeValidator(str)]


class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    email: EmailStr = Field(...)
    password: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    phone_number: Optional[str] = Field(default=None)
    sex: Optional[SexEnum] = Field(default=None)
    roles: List[str] = Field(default=[])
    permissions: List[str] = Field(default=[])
    birthday_date: Optional[datetime.datetime] = Field(default=None)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

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
                "sex": "M",
                "birthday_date": "2004-01-01",
                "roles": ["user"],
                "permissions": ["user:read"],
                "created_at": "20025-01-01",
            }
        },
    )
