from pydantic import BaseModel, Field


class DetailedFeedback(BaseModel):
    task_response: str
    coherence_and_cohesion: str
    lexical_resource: str
    grammatical_range_and_accuracy: str


class SpellingError(BaseModel):
    word: str
    correction: str


class EssayScoreResult(BaseModel):
    overall_band: float = Field(ge=0, le=9)
    task_response_band: float = Field(ge=0, le=9)
    coherence_band: float = Field(ge=0, le=9)
    lexical_band: float = Field(ge=0, le=9)
    grammar_band: float = Field(ge=0, le=9)
    short_feedback: str
    detailed_feedback: DetailedFeedback
    improvement_tips: list[str]
    spelling_errors: list[SpellingError] = Field(default_factory=list)
