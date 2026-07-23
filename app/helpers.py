from datetime import timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasic
from jwt import InvalidTokenError
from starlette import status

from app.crud import demo_db
from app.utils import validate_password, decode_jwt, encode_jwt
from app.shemas import SUser
from app.config import settings

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
    expire_minutes: int = settings.access_token_expire_minutes,
    expire_delta: timedelta | None = None,
):
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload, expire_minutes=expire_minutes, expire_delta=expire_delta
    )


def validate_auth_user(form_data: OAuth2PasswordRequestForm = Depends()):
    if not (user := demo_db.get(form_data.username)):
        raise unauthed_exp
    if not (
        validate_password(
            password=form_data.password,
            hashed_password=user.password,
        )
    ):
        raise unauthed_exp
    if not user.is_active:
        raise unauthed_exp

    return user


def create_access_token(user: SUser = Depends(validate_auth_user)):
    jwt_payload = {"sub": user.username, "username": user.username, "email": user.email}
    return create_token(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(user: SUser = Depends(validate_auth_user)):
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
