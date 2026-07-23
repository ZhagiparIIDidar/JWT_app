from datetime import timedelta, datetime

import jwt
import bcrypt

from app.config import settings


def encode_jwt(
    payload: dict,
    private_key = settings.private_key_path.read_text(),
    algorithm = settings.algorithm,
    expire_minutes: int = settings.access_token_expire_minutes,
    expire_delta: timedelta | None = None
):
    to_encoded = payload.copy()
    now = datetime.utcnow()
    if expire_delta:
        expire = now + expire_delta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encoded.update(
        exp=expire,
        iat=now
    )
    encoded = jwt.encode(
        to_encoded,
        private_key,
        algorithm=algorithm
    )
    return encoded

def decode_jwt(
    token: str | dict,
    public_key=settings.public_key_path.read_text(),
    algorithm=settings.algorithm
):
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )
    return decoded


def hash_password(
        password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)

def validate_password(
        password: str,
        hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )