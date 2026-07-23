from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasic
from jwt import InvalidTokenError
from starlette import status

from app import crud
from app.crud import create_user
from app.models import UsersORM
from app.utils import validate_password, decode_jwt, encode_jwt, hash_password
from app.schemas import SUser, SUserBase
from app.config import settings
from app.database import SessionDep

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

https_basic = HTTPBasic()
o_auth_pwd = OAuth2PasswordBearer(tokenUrl="/auth-jwt/login")


unauthed_exp = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"invalid username or password",
)


def create_token(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_delta: timedelta | None = None,
):
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload, expire_minutes=expire_minutes, expire_delta=expire_delta
    )


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

# Предполагаем, что у тебя есть:
# - SUser — Pydantic схема пользователя (response model)
# - User — SQLAlchemy модель
# - get_password_hash, verify_password — функции для паролей
# - create_access_token, create_refresh_token


async def login_or_register(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> SUser:
    """
    Логинит пользователя.
    Если пользователя нет в базе — автоматически создаёт его.
    """

    # Ищем пользователя по username
    result = await session.execute(
        select(UsersORM).where(UsersORM.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    if user is None:
        new_user = await create_user(
            session=session,
            user_data=SUserBase(
                username=form_data.username,
            ),
            hashed_password=hash_password(form_data.password),
        )

        return new_user

    # Пользователь существует — проверяем пароль
    if not validate_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_tokens(user: Annotated[SUser, Depends(login_or_register)]):
    # Здесь генерируешь access_token и refresh_token
    return {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
    }


def create_access_token(user: SUser = Depends(login_or_register)):
    jwt_payload = {"sub": user.username, "username": user.username, "email": user.email}
    return create_token(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(user: SUser = Depends(login_or_register)):
    jwt_payload = {
        "sub": user.username,
    }
    return create_token(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_delta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )


def get_payload_current_user(
    token: str = Depends(o_auth_pwd),
):
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"123{e}",
        )
    return payload


def get_auth_user_by_sub(payload: dict) -> SUser:
    username = payload.get("sub")
    if user := demo_db.get(username):
        if user.is_active:
            return user
    raise unauthed_exp


def get_auth_user_from_token_type(token_type: str):
    def get_current_user_from_token(
        payload: dict = Depends(get_payload_current_user),
    ):
        token_type_payload = payload.get(TOKEN_TYPE_FIELD)
        if token_type_payload != token_type:
            raise unauthed_exp
        return get_auth_user_by_sub(payload)

    return get_current_user_from_token


class GetterUserFromTokenOfType:
    def __init__(self, token_type: str):
        self.token_type = token_type

    def __call__(self, payload: dict = Depends(get_payload_current_user)):
        token_type_payload = payload.get(TOKEN_TYPE_FIELD)
        if token_type_payload != self.token_type:
            raise unauthed_exp
        return get_auth_user_by_sub(payload)


get_current_user_for_refresh = GetterUserFromTokenOfType(REFRESH_TOKEN_TYPE)
get_current_user = GetterUserFromTokenOfType(ACCESS_TOKEN_TYPE)
