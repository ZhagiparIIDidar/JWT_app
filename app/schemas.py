from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class SUserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None


class SUserCreate(SUserBase):
    password: str


class SUser(SUserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SUserInDB(SUserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hashed_password: str


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
