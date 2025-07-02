import datetime
from typing import Annotated

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


PyObjectId = Annotated[str, BeforeValidator(str)]


class AccessTokenModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    token: str = Field(...)
    user_id: PyObjectId
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    expires_at: datetime.datetime = Field(...)
    revoked: bool = Field(default=False)

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={ObjectId: str},
        validate_by_name=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "685f420bf748b6ad4f8317b5",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user_id": "665e083d1322a68c63f3b8e5",
                "created_at": "2025-06-28T00:00:00Z",
                "expires_at": "2025-06-28T00:00:00Z",
                "revoked": False,
            }
        },
    )
