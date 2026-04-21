from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.essay_submission import SubmissionStatus
from app.schemas.llm import DetailedFeedback, SpellingError


class EssayEvaluateRequest(BaseModel):
    prompt_id: str
    essay_text: str = Field(min_length=20, max_length=20000)
    timer_enabled: bool = False
    timer_duration_seconds: int | None = Field(default=None, ge=1)
    timer_expired: bool = False


class AnonEssayEvaluateRequest(BaseModel):
    topic_text: str = Field(min_length=10, max_length=2000)
    essay_text: str = Field(min_length=20, max_length=20000)
    timer_enabled: bool = False
    timer_duration_seconds: int | None = Field(default=None, ge=1)
    timer_expired: bool = False
    analysis_language: str = Field(default="en", max_length=16)


class EssayEvaluateResponse(BaseModel):
    submission_id: str
    word_count: int
    overall_band: float
    task_response_band: float
    coherence_band: float
    lexical_band: float
    grammar_band: float
    short_feedback: str
    detailed_feedback: DetailedFeedback
    improvement_tips: list[str]
    spelling_errors: list[SpellingError] = Field(default_factory=list)


class EssaySubmissionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    prompt_id: str
    word_count: int
    overall_band: float | None
    short_feedback: str | None
    status: SubmissionStatus
    created_at: datetime


class EssaySubmissionDetail(BaseModel):
    id: str
    prompt_id: str
    prompt_text: str
    essay_text: str
    word_count: int
    timer_enabled: bool
    timer_duration_seconds: int | None
    timer_expired: bool
    overall_band: float | None
    task_response_band: float | None
    coherence_band: float | None
    lexical_band: float | None
    grammar_band: float | None
    short_feedback: str | None
    analysis_json: dict | None
    status: SubmissionStatus
    created_at: datetime
