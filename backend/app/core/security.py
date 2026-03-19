from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# bcrypt only hashes the first 72 bytes; bcrypt 4+ raises if the secret is longer
_BCRYPT_MAX_BYTES = 72


def _password_bytes(password: str) -> bytes:
    b = password.encode("utf-8")
    if len(b) > _BCRYPT_MAX_BYTES:
        return b[:_BCRYPT_MAX_BYTES]
    return b


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            _password_bytes(plain_password),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def create_token(subject: str, expires_minutes: int, token_type: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire, "type": token_type}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
