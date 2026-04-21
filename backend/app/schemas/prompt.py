from pydantic import BaseModel, ConfigDict, Field

from app.models.essay_prompt import PromptSource


class PromptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    topic_text: str
    source: PromptSource


class PromptGenerateRequest(BaseModel):
    mode: str = "generated"


class ManualPromptCreate(BaseModel):
    topic_text: str = Field(min_length=10, max_length=1000)
