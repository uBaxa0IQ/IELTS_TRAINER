from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.essay_submission import EssaySubmission, SubmissionStatus
from app.models.user import User
from app.schemas.analytics import ProgressPoint, ProgressResponse


def get_progress_data(db: Session, user: User) -> ProgressResponse:
    rows = db.scalars(
        select(EssaySubmission)
        .where(EssaySubmission.user_id == user.id, EssaySubmission.status == SubmissionStatus.SCORED)
        .order_by(EssaySubmission.created_at.asc())
    ).all()
    return ProgressResponse(
        points=[
            ProgressPoint(
                submission_id=row.id,
                created_at=row.created_at,
                overall_band=row.overall_band or 0.0,
            )
            for row in rows
            if row.overall_band is not None
        ]
    )
