from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import ProgressResponse
from app.services.analytics_service import get_progress_data


router = APIRouter()


@router.get("/progress", response_model=ProgressResponse)
def progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    return get_progress_data(db, current_user)
