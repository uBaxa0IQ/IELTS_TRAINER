from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserPreferencesPatch, UserRead
from app.services.auth_service import authenticate_user, register_user, update_user_preferences


router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    return register_user(payload, db)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    return authenticate_user(payload, db)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
def patch_me(
    payload: UserPreferencesPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    return UserRead.model_validate(update_user_preferences(payload, current_user, db))
