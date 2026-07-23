from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.schemas import SUser, TokenInfo
from app.helpers import (
    create_access_token,
    create_refresh_token,
    validate_auth_user,
    get_current_user_for_refresh,
    get_current_user,
    get_tokens,
)

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix="/auth-jwt",
    tags=["Authentication"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/login")
def get_tokens(tokens: TokenInfo = Depends(get_tokens)):
    return tokens


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
