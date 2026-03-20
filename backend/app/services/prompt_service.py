import random

from sqlalchemy.orm import Session

from app.integrations.llm.factory import LlmClientFactory
from app.models.essay_prompt import EssayPrompt, PromptSource
from app.models.user import User
from app.schemas.prompt import ManualPromptCreate


FALLBACK_TOPICS = [
    "Some people think that children should begin learning a foreign language at primary school rather than secondary school. Discuss both views and give your own opinion.",
    "Many believe that governments should spend more money on public transport instead of building new roads. To what extent do you agree or disagree?",
    "In many countries, young people are encouraged to work or travel for a year before university. Do the advantages outweigh the disadvantages?",
]

GLOBAL_TOPIC_DOMAINS = [
    "education policy and access",
    "technology and digital life",
    "environment and sustainability",
    "public health and lifestyle",
    "work, careers, and automation",
    "urban life and transport",
    "media, advertising, and culture",
    "family, youth, and social values",
    "economy, taxation, and public spending",
]

IELTS_TASK2_TYPES = [
    "opinion (To what extent do you agree or disagree?)",
    "discussion (Discuss both views and give your opinion.)",
    "advantages/disadvantages (Do the advantages outweigh the disadvantages?)",
    "problem/solution (What are the problems and what solutions can you suggest?)",
    "direct questions (Answer both questions.)",
]


def _build_topic_constraints() -> tuple[str, str]:
    domain = random.choice(GLOBAL_TOPIC_DOMAINS)
    question_type = random.choice(IELTS_TASK2_TYPES)
    constraints = (
        f"Use this global domain: {domain}\n"
        f"Use this IELTS Task 2 question type: {question_type}\n"
        "Return exactly one original topic. Do not repeat recent common templates."
    )
    return constraints, f"domain:{domain};type:{question_type}"


def create_generated_prompt(db: Session) -> EssayPrompt:
    client = LlmClientFactory.create()
    constraints, tags = _build_topic_constraints()
    topic_text = client.generate_topic(topic_constraints=constraints)
    prompt = EssayPrompt(topic_text=topic_text, source=PromptSource.GENERATED, tags=tags)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def create_fallback_prompt(db: Session) -> EssayPrompt:
    existing = db.query(EssayPrompt).filter(EssayPrompt.source == PromptSource.PRESET).first()
    if existing is not None:
        return existing

    prompt = EssayPrompt(topic_text=FALLBACK_TOPICS[0], source=PromptSource.PRESET)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def get_or_generate_prompt(db: Session) -> EssayPrompt:
    try:
        return create_generated_prompt(db)
    except Exception:
        # Failed flush/commit leaves the session in "needs rollback" state; clear it before fallback.
        db.rollback()
        return create_fallback_prompt(db)


def create_manual_prompt(payload: ManualPromptCreate, db: Session, user: User) -> EssayPrompt:
    prompt = EssayPrompt(
        topic_text=payload.topic_text.strip(),
        source=PromptSource.MANUAL,
        created_by_user_id=user.id,
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt
