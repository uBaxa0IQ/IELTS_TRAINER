from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserPreferencesPatch, UserRead


def build_token_response(user: User) -> TokenResponse:
    ensure_user_nickname(user)
    access_token = create_token(user.id, settings.access_token_minutes, "access")
    refresh_token = create_token(user.id, settings.refresh_token_minutes, "refresh")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


def refresh_access_token(refresh_token: str, db: Session) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user = db.get(User, sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    ensure_user_nickname(user)
    access_token = create_token(user.id, settings.access_token_minutes, "access")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


def normalize_nickname(raw: str) -> str:
    # Keep it simple: letters/digits + `_`/`-`, trim length.
    n = raw.strip().replace(" ", "_")
    n = "".join(ch for ch in n if ch.isalnum() or ch in {"_", "-"})
    if not n:
        return "user"
    return n[:32]


def derive_nickname_from_email(email: str) -> str:
    local_part = email.split("@", 1)[0] if "@" in email else email
    return normalize_nickname(local_part or "user")


def derive_nickname_from_google(payload: dict[str, Any]) -> str | None:
    name = payload.get("name")
    if isinstance(name, str) and name.strip():
        return normalize_nickname(name)
    # Some providers may return email without a profile name.
    email = payload.get("email")
    if isinstance(email, str) and email.strip():
        return derive_nickname_from_email(email)
    return None


def ensure_user_nickname(user: User) -> None:
    if user.nickname and user.nickname.strip():
        user.nickname = normalize_nickname(user.nickname)
        return
    user.nickname = derive_nickname_from_email(user.email)


def register_user(payload: UserCreate, db: Session) -> TokenResponse:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        nickname=derive_nickname_from_email(payload.email),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return build_token_response(user)


def authenticate_user(payload: UserCreate, db: Session) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or user.password_hash is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return build_token_response(user)


def update_user_preferences(payload: UserPreferencesPatch, user: User, db: Session) -> User:
    if payload.analysis_language is not None:
        user.analysis_language = payload.analysis_language
    if payload.nickname is not None:
        user.nickname = normalize_nickname(payload.nickname)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_google_user(payload: dict[str, Any], db: Session) -> tuple[User, bool]:
    """
    Google OAuth user upsert by stable `sub`.

    Expected payload fields (OpenID Connect):
    - `sub`: stable user identifier
    - `email`: email address
    - `name`: display name (optional)
    """
    google_sub = payload.get("sub")
    email = payload.get("email")

    if not isinstance(google_sub, str) or not google_sub.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Google subject")
    if not isinstance(email, str) or not email.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google email is required")

    existing = db.scalar(select(User).where(User.google_sub == google_sub))
    created = False
    if existing is None:
        # Fallback: if the email already exists, link it to this Google account.
        existing = db.scalar(select(User).where(User.email == email))

    if existing is None:
        created = True
        user = User(
            email=email,
            password_hash=None,
            google_sub=google_sub,
            nickname=derive_nickname_from_google(payload),
        )
        ensure_user_nickname(user)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user, created

    # Link existing user to Google provider.
    existing.google_sub = google_sub
    if not existing.nickname:
        existing.nickname = derive_nickname_from_google(payload)
    db.commit()
    db.refresh(existing)
    ensure_user_nickname(existing)
    return existing, created
