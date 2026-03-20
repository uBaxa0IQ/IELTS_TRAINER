from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.analysis_language import ALLOWED_ANALYSIS_LANGUAGES


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    nickname: str | None = None
    analysis_language: str = "en"


class UserPreferencesPatch(BaseModel):
    analysis_language: str | None = None
    nickname: str | None = None

    @field_validator("analysis_language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        if v is None:
            return None
        c = v.strip().lower()
        if c not in ALLOWED_ANALYSIS_LANGUAGES:
            raise ValueError("Unsupported analysis language")
        return c

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, v: str | None) -> str | None:
        if v is None:
            return None
        n = v.strip()
        if len(n) < 2:
            raise ValueError("Nickname is too short")
        if len(n) > 32:
            raise ValueError("Nickname is too long")
        return n


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)
