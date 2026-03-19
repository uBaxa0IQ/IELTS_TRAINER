from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.prompt import ManualPromptCreate, PromptGenerateRequest, PromptRead
from app.services.prompt_service import create_manual_prompt, get_or_generate_prompt


router = APIRouter()


@router.post("/generate", response_model=PromptRead)
def generate_prompt(
    _: PromptGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptRead:
    prompt = get_or_generate_prompt(db)
    return PromptRead.model_validate(prompt)


@router.post("/generate-anon", response_model=PromptRead)
def generate_prompt_anonymous(
    db: Session = Depends(get_db),
) -> PromptRead:
    prompt = get_or_generate_prompt(db)
    return PromptRead.model_validate(prompt)


@router.post("/manual", response_model=PromptRead)
def manual_prompt(
    payload: ManualPromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptRead:
    prompt = create_manual_prompt(payload, db, current_user)
    return PromptRead.model_validate(prompt)
