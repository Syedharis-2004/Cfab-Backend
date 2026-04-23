from beanie import Document, Indexed
from typing import Optional

class User(Document):
    name: str
    email: Indexed(str, unique=True)
    hashed_password: str

    class Settings:
        name = "users"
