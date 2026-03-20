import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PromptSource(str, Enum):
    PRESET = "preset"
    GENERATED = "generated"
    MANUAL = "manual"


class EssayPrompt(Base):
    __tablename__ = "essay_prompts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    topic_text: Mapped[str] = mapped_column(Text())
    # Persist enum .value ("preset") so it matches PostgreSQL native enum labels from Alembic.
    source: Mapped[PromptSource] = mapped_column(
        SqlEnum(PromptSource, values_callable=lambda x: [e.value for e in x]),
        index=True,
    )
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    submissions = relationship("EssaySubmission", back_populates="prompt")
