from typing import Any, Literal

from pydantic import BaseModel, Field


AnalyticsEventType = Literal["signup_google", "login_google", "topic_generated", "essay_evaluated"]


class AnalyticsEventCreate(BaseModel):
    event_type: AnalyticsEventType
    meta: dict[str, Any] = Field(default_factory=dict)

