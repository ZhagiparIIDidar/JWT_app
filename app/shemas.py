import datetime

from pydantic import BaseModel, EmailStr


class SAddUser(BaseModel):
    username: str
    password: bytes
    email: str | None = None


class SUser(SAddUser):
    is_active: bool = True


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
