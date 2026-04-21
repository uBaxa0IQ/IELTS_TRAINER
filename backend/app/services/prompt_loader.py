from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(*parts: str) -> str:
    path = PROMPTS_DIR.joinpath(*parts)
    return path.read_text(encoding="utf-8")
