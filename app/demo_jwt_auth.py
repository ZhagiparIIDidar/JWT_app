from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from shemas import SUser, TokenInfo
from helpers import (
    create_access_token,
    create_refresh_token,
    validate_auth_user,
    get_current_user_for_refresh,
    get_current_user,
)

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix="/auth-jwt",
    tags=["Authentication"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/login")
def get_tokens(user: SUser = Depends(validate_auth_user)):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
def refresh_access_token(
    user: SUser = Depends(get_current_user_for_refresh),
):
    access_token = create_access_token(user)
    return {"access_token": access_token, "refresh_token": None}


@router.post("/me")
def get_user(user: SUser = Depends(get_current_user)):
    return {
        "username": user.username,
        "password": user.password,
        "email": user.email,
    }
