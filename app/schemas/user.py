from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: PydanticObjectId

    class Config:
        from_attributes = True
