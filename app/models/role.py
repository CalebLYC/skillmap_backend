import datetime
from typing import Annotated, List
from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


PyObjectId = Annotated[str, BeforeValidator(str)]


class RoleModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    permissions: List[str] = Field(default=[])
    inherited_roles: List[str] = Field(default=[])
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
                "name": "user",
                "permissions": ["user:read"],
                "inherited_roles": ["role"],
            }
        },
    )


class PermissionModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    code: str = Field(...)
    description: str = Field(...)
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
                "code": "user:read",
                "description": "Read user",
            }
        },
    )
