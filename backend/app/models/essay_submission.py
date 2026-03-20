import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, Enum as SqlEnum, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    SCORED = "scored"
    FAILED = "failed"


class EssaySubmission(Base):
    __tablename__ = "essay_submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    prompt_id: Mapped[str] = mapped_column(String(36), ForeignKey("essay_prompts.id"), index=True)
    essay_text: Mapped[str] = mapped_column(Text())
    word_count: Mapped[int] = mapped_column(default=0)
    timer_enabled: Mapped[bool] = mapped_column(Boolean(), default=False)
    timer_duration_seconds: Mapped[int | None] = mapped_column(nullable=True)
    timer_expired: Mapped[bool] = mapped_column(Boolean(), default=False)
    task_response_band: Mapped[float | None] = mapped_column(Float(), nullable=True)
    coherence_band: Mapped[float | None] = mapped_column(Float(), nullable=True)
    lexical_band: Mapped[float | None] = mapped_column(Float(), nullable=True)
    grammar_band: Mapped[float | None] = mapped_column(Float(), nullable=True)
    overall_band: Mapped[float | None] = mapped_column(Float(), nullable=True)
    short_feedback: Mapped[str | None] = mapped_column(Text(), nullable=True)
    analysis_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[SubmissionStatus] = mapped_column(
        SqlEnum(SubmissionStatus, values_callable=lambda x: [e.value for e in x]),
        default=SubmissionStatus.PENDING,
    )
    failure_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="submissions")
    prompt = relationship("EssayPrompt", back_populates="submissions")
