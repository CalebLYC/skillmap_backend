import datetime
from typing import Annotated, List
from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


PyObjectId = Annotated[str, BeforeValidator(str)]


class RoleCreateSchema(BaseModel):
    name: str = Field(...)
    permissions: List[str] = Field(default=[])
    inherited_roles: List[str] = Field(default=[])

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "user",
                "permissions": ["user:read"],
                "inherited_roles": ["role"],
            }
        },
    )


class RoleReadSchema(RoleCreateSchema):
    id: str = Field(..., alias="_id", serialization_alias="id")
    created_at: datetime.datetime = Field(...)

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "id": "685f420bf748b6ad4f8317b5",
                "name": "user",
                "permissions": ["user:read"],
                "inherited_roles": ["role"],
                "created_at": "20025-01-01",
            }
        },
    )


class PermissionCreateSchema(BaseModel):
    code: str = Field(...)
    description: str = Field(...)
    created_at: datetime.datetime = Field(...)

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "code": "user:read",
                "description": "Read user",
            }
        },
    )


class PermissionReadSchema(PermissionCreateSchema):
    id: str = Field(..., alias="_id", serialization_alias="id")

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "id": "685f420bf748b6ad4f8317b5",
                "code": "user:read",
                "description": "Read user",
                "created_at": "20025-01-01",
            }
        },
    )
