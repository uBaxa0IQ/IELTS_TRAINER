from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.analytics_event import AnalyticsEvent
from app.schemas.analytics import ProgressResponse
from app.schemas.analytics_events import AnalyticsEventCreate
from app.services.analytics_service import get_progress_data


router = APIRouter()


@router.get("/progress", response_model=ProgressResponse)
def progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    return get_progress_data(db, current_user)


@router.post("/events")
def create_analytics_event(
    payload: AnalyticsEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    event = AnalyticsEvent(user_id=current_user.id, event_type=payload.event_type, meta=payload.meta)
    db.add(event)
    db.commit()
    return {"ok": "true"}
