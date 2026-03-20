import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # For Google-only accounts we might not have a password.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Displayed name in the UI (nickname).
    nickname: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    # Stable Google account identifier.
    google_sub: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True, index=True)
    analysis_language: Mapped[str] = mapped_column(String(16), default="en", server_default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    submissions = relationship("EssaySubmission", back_populates="user")
