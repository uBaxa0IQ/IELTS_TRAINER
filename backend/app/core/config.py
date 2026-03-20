from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/ielts_trainer",
        alias="DATABASE_URL",
    )
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_minutes: int = Field(default=60, alias="ACCESS_TOKEN_MINUTES")
    refresh_token_minutes: int = Field(default=60 * 24 * 7, alias="REFRESH_TOKEN_MINUTES")
    cors_origins: list[str] = Field(default=["http://localhost:5173"], alias="CORS_ORIGINS")

    llm_provider: str = Field(default="mock", alias="LLM_PROVIDER")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_endpoint: str | None = Field(default=None, alias="LLM_ENDPOINT")
    llm_model: str = Field(default="mock-ielts", alias="LLM_MODEL")
    llm_timeout_seconds: int = Field(default=30, alias="LLM_TIMEOUT_SECONDS")

    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")

    # Google OAuth (optional until configured).
    google_client_id: str | None = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: str | None = Field(default=None, alias="GOOGLE_CLIENT_SECRET")
    # If not provided, redirect_uri is derived from the incoming request URL.
    google_redirect_uri: str | None = Field(default=None, alias="GOOGLE_REDIRECT_URI")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
