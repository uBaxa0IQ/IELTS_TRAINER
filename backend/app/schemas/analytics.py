from datetime import datetime

from pydantic import BaseModel


class ProgressPoint(BaseModel):
    submission_id: str
    created_at: datetime
    overall_band: float


class ProgressResponse(BaseModel):
    points: list[ProgressPoint]
