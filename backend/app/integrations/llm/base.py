from abc import ABC, abstractmethod

from app.schemas.llm import EssayScoreResult


class BaseLlmClient(ABC):
    @abstractmethod
    def generate_topic(self, *, topic_constraints: str | None = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def score_essay(self, topic: str, essay_text: str, *, language: str = "en") -> EssayScoreResult:
        raise NotImplementedError
