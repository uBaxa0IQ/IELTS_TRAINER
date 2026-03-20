from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserPreferencesPatch, UserRead
from app.services.auth_service import (
    build_token_response,
    ensure_user_nickname,
    get_or_create_google_user,
    update_user_preferences,
)

import httpx
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token as google_id_token


router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    raise HTTPException(status_code=404, detail="Email/password registration is disabled. Use Google OAuth.")


@router.post("/login", response_model=TokenResponse)
def login(payload: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    raise HTTPException(status_code=404, detail="Email/password login is disabled. Use Google OAuth.")


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    ensure_user_nickname(current_user)
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
def patch_me(
    payload: UserPreferencesPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    return UserRead.model_validate(update_user_preferences(payload, current_user, db))


@router.get("/google/login")
def google_login(request: Request) -> RedirectResponse:
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured")

    redirect_uri = settings.google_redirect_uri
    if not redirect_uri:
        # Derived from the incoming request URL (works for local dev).
        redirect_uri = str(request.url_for("google_callback"))

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        # Helps reduce accidental account switching.
        "prompt": "select_account",
        # Some flows require explicit offline access for refresh token, but we only use id token.
        "access_type": "offline",
    }
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    return RedirectResponse(url=f"{google_auth_url}?{urlencode(params)}", status_code=302)


@router.get("/google/callback", name="google_callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth code")
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured")

    redirect_uri = settings.google_redirect_uri
    if not redirect_uri:
        redirect_uri = str(request.url_for("google_callback"))

    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
        )

    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Google token exchange failed")

    token_data = token_resp.json()
    id_token = token_data.get("id_token")
    if not isinstance(id_token, str) or not id_token:
        raise HTTPException(status_code=400, detail="Google id_token is missing")

    google_req = GoogleRequest()
    try:
        decoded = google_id_token.verify_oauth2_token(
            id_token,
            google_req,
            audience=settings.google_client_id,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Google id_token validation failed") from exc

    # decoded: { sub, email, name, ... }
    user, new_user = get_or_create_google_user(decoded, db)
    token_response = build_token_response(user)

    redirect_params = {"token": token_response.access_token, "new_user": "1" if new_user else "0"}
    frontend_url = settings.frontend_url.rstrip("/")
    callback_url = f"{frontend_url}/auth/google/callback?{urlencode(redirect_params)}"
    return RedirectResponse(url=callback_url, status_code=302)
