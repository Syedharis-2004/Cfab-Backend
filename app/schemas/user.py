from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "user"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str

    class Config:
        from_attributes = True
