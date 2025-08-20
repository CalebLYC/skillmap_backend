import datetime
from pydantic import BaseModel, ConfigDict, Field


class AccessTokenCreateSchema(BaseModel):
    token: str = Field(...)
    user_id: str = Field(..., alias="_id", serialization_alias="id")

    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user_id": "665e083d1322a68c63f3b8e5",
            }
        },
    )


class AccessTokenReadSchema(BaseModel):
    id: str = Field(..., alias="_id", serialization_alias="id")
    token: str = Field(...)
    user_id: str = Field(..., alias="_id", serialization_alias="id")
    created_at: datetime.datetime = Field(...)
    expires_at: datetime.datetime
    revoked: bool = Field(default=False)

    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user_id": "665e083d1322a68c63f3b8e5",
            }
        },
    )
