import json

import httpx

from app.core.config import settings
from app.integrations.llm.base import BaseLlmClient
from app.core.analysis_language import language_instruction_for_prompt
from app.schemas.llm import EssayScoreResult
from app.services.prompt_loader import load_prompt


class YandexLlmClient(BaseLlmClient):
    DEFAULT_OPENAI_COMPAT_ENDPOINT = "https://llm.api.cloud.yandex.net/v1/chat/completions"

    def __init__(self) -> None:
        if not settings.llm_api_key:
            raise ValueError("LLM API key must be configured")
        if not settings.llm_model:
            raise ValueError("LLM model must be configured")

    def generate_topic(self, *, topic_constraints: str | None = None) -> str:
        prompt = load_prompt("topic_generation", "system.txt")
        if topic_constraints:
            prompt = f"{prompt}\n\nGeneration constraints:\n{topic_constraints.strip()}"
        payload = self._build_payload(
            system_prompt=(
                "You generate realistic IELTS Writing Task 2 prompts. "
                "Prioritize diversity across social, technology, environment, education, health, work, and culture topics."
            ),
            user_prompt=prompt,
            temperature=0.85,
            max_tokens=220,
        )
        data = self._post(payload)
        return self._extract_text(data)

    def score_essay(self, topic: str, essay_text: str, *, language: str = "en") -> EssayScoreResult:
        rubric = load_prompt("shared", "ielts_rubric.txt")
        json_contract = load_prompt("shared", "json_contract.txt")
        language_instruction = language_instruction_for_prompt(language)
        system_prompt = load_prompt("essay_scoring", "system.txt").format(
            rubric=rubric,
            json_contract=json_contract,
            topic=topic,
            essay_text=essay_text,
            language_instruction=language_instruction,
        )
        payload = self._build_payload(
            system_prompt="Return only valid JSON that strictly matches the requested schema.",
            user_prompt=system_prompt,
        )
        data = self._post(payload)
        content = self._extract_text(data)
        return EssayScoreResult.model_validate(json.loads(content))

    def _build_payload(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> dict:
        return {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    def _post(self, payload: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "x-data-logging-enabled": "false",
        }
        folder_id = self._extract_folder_id(settings.llm_model)
        if folder_id:
            headers["x-folder-id"] = folder_id

        endpoint = settings.llm_endpoint or self.DEFAULT_OPENAI_COMPAT_ENDPOINT
        if "foundationModels" in endpoint:
            endpoint = self.DEFAULT_OPENAI_COMPAT_ENDPOINT

        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    def _extract_text(self, data: dict) -> str:
        if "choices" in data and data["choices"]:
            choice = data["choices"][0]
            if isinstance(choice, dict):
                if "message" in choice and isinstance(choice["message"], dict):
                    return str(choice["message"].get("content", ""))
                if "text" in choice:
                    return str(choice["text"])
        raise ValueError("Unsupported provider response format")

    def _extract_folder_id(self, model_uri: str) -> str | None:
        prefix = "gpt://"
        if not model_uri.startswith(prefix):
            return None
        remainder = model_uri[len(prefix) :]
        parts = remainder.split("/", 1)
        return parts[0] if parts and parts[0] else None
