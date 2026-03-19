from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.essay_submission import EssaySubmission
from app.models.user import User
from app.schemas.essay import (
    AnonEssayEvaluateRequest,
    EssayEvaluateRequest,
    EssayEvaluateResponse,
    EssaySubmissionDetail,
    EssaySubmissionListItem,
)
from app.services.essay_service import evaluate_anonymous, evaluate_submission, get_submission_detail


router = APIRouter()


@router.post("/evaluate", response_model=EssayEvaluateResponse)
def evaluate_essay(
    payload: EssayEvaluateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EssayEvaluateResponse:
    return evaluate_submission(payload, db, current_user)


@router.post("/evaluate-anon", response_model=EssayEvaluateResponse)
def evaluate_essay_anonymous(
    payload: AnonEssayEvaluateRequest,
) -> EssayEvaluateResponse:
    return evaluate_anonymous(payload)


@router.get("", response_model=list[EssaySubmissionListItem])
def list_essays(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EssaySubmissionListItem]:
    rows = db.scalars(
        select(EssaySubmission)
        .where(EssaySubmission.user_id == current_user.id)
        .order_by(EssaySubmission.created_at.desc())
    ).all()
    return [EssaySubmissionListItem.model_validate(row) for row in rows]


@router.get("/{submission_id}", response_model=EssaySubmissionDetail)
def essay_detail(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EssaySubmissionDetail:
    return get_submission_detail(submission_id, db, current_user)
