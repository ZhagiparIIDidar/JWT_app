from pydantic import BaseModel, EmailStr, ConfigDict


class SUserBase(BaseModel):
    username: str
    email: EmailStr


class SUserCreate(SUserBase):
    password: str


class SUser(SUserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

class SUserInDB(SUserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hashed_password: str