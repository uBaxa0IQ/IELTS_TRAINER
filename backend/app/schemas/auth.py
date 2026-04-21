from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.analysis_language import ALLOWED_ANALYSIS_LANGUAGES


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    analysis_language: str = "en"


class UserPreferencesPatch(BaseModel):
    analysis_language: str | None = None

    @field_validator("analysis_language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        if v is None:
            return None
        c = v.strip().lower()
        if c not in ALLOWED_ANALYSIS_LANGUAGES:
            raise ValueError("Unsupported analysis language")
        return c


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead
