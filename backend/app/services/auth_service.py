from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserPreferencesPatch, UserRead


def build_token_response(user: User) -> TokenResponse:
    access_token = create_token(user.id, settings.access_token_minutes, "access")
    refresh_token = create_token(user.id, settings.refresh_token_minutes, "refresh")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


def register_user(payload: UserCreate, db: Session) -> TokenResponse:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return build_token_response(user)


def authenticate_user(payload: UserCreate, db: Session) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return build_token_response(user)


def update_user_preferences(payload: UserPreferencesPatch, user: User, db: Session) -> User:
    if payload.analysis_language is not None:
        user.analysis_language = payload.analysis_language
    db.commit()
    db.refresh(user)
    return user
