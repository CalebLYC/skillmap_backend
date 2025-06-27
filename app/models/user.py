from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId


class PyObjectId(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    full_name: Optional[str]


class UserInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
