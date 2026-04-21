import json
import sys
from pathlib import Path
from urllib import request


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"

# This endpoint matches the format the project uses for chat completions:
# `https://llm.api.cloud.yandex.net/v1/chat/completions`
# and typically also supports listing models at `/v1/models`.
MODELS_URL = "https://llm.api.cloud.yandex.net/v1/models"


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


def main() -> int:
    env = load_env(ENV_PATH)
    api_key = env.get("LLM_API_KEY", "").strip()

    if not api_key:
        print("Missing LLM_API_KEY in .env")
        return 1

    # Optional CLI filter: python scripts/list_models.py qwen
    # If empty, prints everything available.
    substring = (sys.argv[1].strip().lower() if len(sys.argv) > 1 else "")

    def fetch_with_auth(auth_header_value: str) -> dict:
        req = request.Request(MODELS_URL, method="GET")
        req.add_header("Authorization", auth_header_value)
        with request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body)

    data: dict
    # For llm.api.cloud.yandex.net, OpenAI-compatible endpoints usually expect Bearer.
    auth_variants = [f"Bearer {api_key}", f"Api-Key {api_key}"]
    last_error: Exception | None = None
    for auth_value in auth_variants:
        try:
            data = fetch_with_auth(auth_value)
            last_error = None
            break
        except Exception as exc:
            last_error = exc
            print(f"Request with Authorization={auth_value!r} failed.")
            # urllib.error.HTTPError has .read() with details
            if hasattr(exc, "read"):
                try:
                    details = exc.read().decode("utf-8", errors="replace")
                    print(details)
                except Exception:
                    pass

    if last_error is not None:
        raise SystemExit(1)

    items = data.get("data", [])
    if not isinstance(items, list):
        print("Unexpected response format: 'data' is not a list")
        return 1

    filtered: list[dict] = []
    for m in items:
        if not isinstance(m, dict):
            continue
        model_id = str(m.get("id", "") or "")
        if substring and substring not in model_id.lower():
            continue
        filtered.append(m)

    print(f"Total models returned: {len(items)}")
    print(f"After filter: {len(filtered)} (substring={substring!r})")
    print("")

    # Print as "id" lines so you can paste into LLM_MODEL directly.
    for m in filtered:
        model_id = m.get("id")
        metadata = m.get("metadata") or {}
        name = metadata.get("name")
        mtype = metadata.get("type")
        if name or mtype:
            print(f"{model_id}  # {name or ''} ({mtype or 'type?'})")
        else:
            print(f"{model_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

