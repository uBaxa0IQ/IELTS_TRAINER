import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.analysis_language import normalize_analysis_language
from app.integrations.llm.factory import LlmClientFactory
from app.models.essay_prompt import EssayPrompt
from app.models.essay_submission import EssaySubmission, SubmissionStatus
from app.models.user import User
from app.schemas.essay import (
    AnonEssayEvaluateRequest,
    EssayEvaluateRequest,
    EssayEvaluateResponse,
    EssaySubmissionDetail,
)
from app.schemas.llm import SpellingError


def count_words(text: str) -> int:
    return len([word for word in text.split() if word.strip()])


def evaluate_submission(payload: EssayEvaluateRequest, db: Session, user: User) -> EssayEvaluateResponse:
    prompt = db.scalar(select(EssayPrompt).where(EssayPrompt.id == payload.prompt_id))
    if prompt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    word_count = count_words(payload.essay_text)
    submission = EssaySubmission(
        user_id=user.id,
        prompt_id=prompt.id,
        essay_text=payload.essay_text.strip(),
        word_count=word_count,
        timer_enabled=payload.timer_enabled,
        timer_duration_seconds=payload.timer_duration_seconds,
        timer_expired=payload.timer_expired,
        status=SubmissionStatus.PENDING,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    try:
        client = LlmClientFactory.create()
        lang = normalize_analysis_language(user.analysis_language)
        result = client.score_essay(prompt.topic_text, payload.essay_text, language=lang)
        submission.task_response_band = result.task_response_band
        submission.coherence_band = result.coherence_band
        submission.lexical_band = result.lexical_band
        submission.grammar_band = result.grammar_band
        submission.overall_band = result.overall_band
        submission.short_feedback = result.short_feedback
        submission.analysis_json = result.model_dump()
        submission.status = SubmissionStatus.SCORED
        db.commit()
        db.refresh(submission)
        return EssayEvaluateResponse(
            submission_id=submission.id,
            word_count=word_count,
            overall_band=result.overall_band,
            task_response_band=result.task_response_band,
            coherence_band=result.coherence_band,
            lexical_band=result.lexical_band,
            grammar_band=result.grammar_band,
            short_feedback=result.short_feedback,
            detailed_feedback=result.detailed_feedback,
            improvement_tips=result.improvement_tips,
            spelling_errors=result.spelling_errors,
        )
    except Exception as exc:
        submission.status = SubmissionStatus.FAILED
        submission.failure_reason = str(exc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "SCORING_FAILED", "message": "Unable to score essay right now."},
        ) from exc


def evaluate_anonymous(payload: AnonEssayEvaluateRequest) -> EssayEvaluateResponse:
    """Score an essay without saving to DB (anonymous user)."""
    word_count = count_words(payload.essay_text)
    try:
        client = LlmClientFactory.create()
        lang = normalize_analysis_language(payload.analysis_language)
        result = client.score_essay(payload.topic_text, payload.essay_text, language=lang)
        return EssayEvaluateResponse(
            submission_id=str(uuid.uuid4()),
            word_count=word_count,
            overall_band=result.overall_band,
            task_response_band=result.task_response_band,
            coherence_band=result.coherence_band,
            lexical_band=result.lexical_band,
            grammar_band=result.grammar_band,
            short_feedback=result.short_feedback,
            detailed_feedback=result.detailed_feedback,
            improvement_tips=result.improvement_tips,
            spelling_errors=result.spelling_errors,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "SCORING_FAILED", "message": "Unable to score essay right now."},
        ) from exc


def get_submission_detail(submission_id: str, db: Session, user: User) -> EssaySubmissionDetail:
    submission = db.scalar(
        select(EssaySubmission).where(EssaySubmission.id == submission_id, EssaySubmission.user_id == user.id)
    )
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    prompt = db.get(EssayPrompt, submission.prompt_id)
    return EssaySubmissionDetail(
        id=submission.id,
        prompt_id=submission.prompt_id,
        prompt_text=prompt.topic_text if prompt else "",
        essay_text=submission.essay_text,
        word_count=submission.word_count,
        timer_enabled=submission.timer_enabled,
        timer_duration_seconds=submission.timer_duration_seconds,
        timer_expired=submission.timer_expired,
        overall_band=submission.overall_band,
        task_response_band=submission.task_response_band,
        coherence_band=submission.coherence_band,
        lexical_band=submission.lexical_band,
        grammar_band=submission.grammar_band,
        short_feedback=submission.short_feedback,
        analysis_json=submission.analysis_json,
        status=submission.status,
        created_at=submission.created_at,
    )
