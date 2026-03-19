import json
import sys
from pathlib import Path
from urllib import error, request


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"
OPENAI_COMPAT_ENDPOINT = "https://llm.api.cloud.yandex.net/v1/chat/completions"
LEGACY_ENDPOINT = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def extract_openai_text(data: dict) -> str:
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str):
                    return content

    raise ValueError(
        f"Unsupported OpenAI-compatible response format: {json.dumps(data, ensure_ascii=False)[:400]}"
    )


def extract_legacy_text(data: dict) -> str:
    result = data.get("result")
    if isinstance(result, dict):
        alternatives = result.get("alternatives")
        if isinstance(alternatives, list) and alternatives:
            first = alternatives[0]
            if isinstance(first, dict):
                message = first.get("message")
                if isinstance(message, dict):
                    text = message.get("text")
                    if isinstance(text, str):
                        return text

    if isinstance(result, str):
        return result

    raise ValueError(f"Unsupported legacy response format: {json.dumps(data, ensure_ascii=False)[:400]}")


def extract_folder_id(model_uri: str) -> str | None:
    prefix = "gpt://"
    if not model_uri.startswith(prefix):
        return None
    remainder = model_uri[len(prefix) :]
    parts = remainder.split("/", 1)
    if not parts or not parts[0]:
        return None
    return parts[0]


def extract_model_name(model_uri: str) -> str:
    prefix = "gpt://"
    if not model_uri.startswith(prefix):
        return model_uri
    remainder = model_uri[len(prefix) :]
    parts = remainder.split("/", 1)
    if len(parts) < 2:
        return model_uri
    return parts[1]


def perform_request(url: str, payload: dict, headers: dict[str, str], timeout: int) -> dict:
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def main() -> int:
    env = load_env(ENV_PATH)

    api_key = env.get("LLM_API_KEY")
    model_uri = env.get("LLM_MODEL")
    configured_endpoint = env.get("LLM_ENDPOINT", "").strip()
    timeout = int(env.get("LLM_TIMEOUT_SECONDS", "30"))
    folder_id = env.get("LLM_FOLDER_ID") or extract_folder_id(model_uri or "")
    short_model_name = extract_model_name(model_uri or "")
    configured_is_legacy = "foundationModels" in configured_endpoint

    if not api_key:
        print("Missing LLM_API_KEY in .env")
        return 1
    if not model_uri:
        print("Missing LLM_MODEL in .env")
        return 1

    tests: list[tuple[str, str, dict, dict[str, str], callable]] = []

    if folder_id:
        openai_url = OPENAI_COMPAT_ENDPOINT if not configured_endpoint or configured_is_legacy else configured_endpoint
        common_openai_payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a concise assistant. Reply in plain English text only.",
                },
                {
                    "role": "user",
                    "content": "Reply with one short sentence confirming that the Yandex LLM API is reachable.",
                },
            ],
            "temperature": 0.2,
            "max_tokens": 120,
        }
        openai_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "x-folder-id": folder_id,
            "x-data-logging-enabled": "false",
        }
        fallback_models = [
            ("selected model URI", model_uri),
            ("selected short model name", short_model_name),
            ("fallback yandexgpt-lite", f"gpt://{folder_id}/yandexgpt-lite/latest"),
            ("fallback yandexgpt", f"gpt://{folder_id}/yandexgpt/latest"),
        ]
        for label_suffix, model_value in fallback_models:
            tests.append(
                (
                    f"OpenAI-compatible ({label_suffix})",
                    openai_url,
                    {"model": model_value, **common_openai_payload},
                    openai_headers,
                    extract_openai_text,
                )
            )

    legacy_url = LEGACY_ENDPOINT if not configured_endpoint or not configured_is_legacy else configured_endpoint
    legacy_payload = {
        "modelUri": model_uri,
        "completionOptions": {
            "stream": False,
            "temperature": 0.2,
            "maxTokens": 120,
        },
        "messages": [
            {
                "role": "system",
                "text": "You are a concise assistant. Reply in plain English text only.",
            },
            {
                "role": "user",
                "text": "Reply with one short sentence confirming that the Yandex LLM API is reachable.",
            },
        ],
    }
    legacy_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}",
    }
    tests.append(("Legacy completion", legacy_url, legacy_payload, legacy_headers, extract_legacy_text))

    print("Testing Yandex LLM access...")
    print(f"Model: {model_uri}")
    if folder_id:
        print(f"Folder ID: {folder_id}")

    last_error = None
    for label, endpoint, payload, headers, extractor in tests:
        print(f"\nTrying {label} endpoint:")
        print(f"  {endpoint}")
        try:
            data = perform_request(endpoint, payload, headers, timeout)
            text = extractor(data)
            print("\nSuccess.")
            print(f"Response: {text}")
            return 0
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            print(f"HTTP error: {exc.code}")
            print(details)
            last_error = exc
        except Exception as exc:
            print(f"Request failed: {exc}")
            last_error = exc

    print("\nAll request formats failed.")
    return 1 if last_error else 0


if __name__ == "__main__":
    sys.exit(main())
