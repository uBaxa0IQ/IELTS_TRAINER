from app.core.config import settings
from app.integrations.llm.base import BaseLlmClient
from app.integrations.llm.mock import MockLlmClient
from app.integrations.llm.yandex import YandexLlmClient


class LlmClientFactory:
    @staticmethod
    def create() -> BaseLlmClient:
        provider = settings.llm_provider.lower()
        if provider == "yandex":
            return YandexLlmClient()
        return MockLlmClient()
