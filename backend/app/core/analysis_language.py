"""Preferred language for LLM-written feedback (not the essay language)."""

ALLOWED_ANALYSIS_LANGUAGES: frozenset[str] = frozenset(
    {
        "en",
        "ru",
        "uk",
        "de",
        "fr",
        "es",
        "pt",
        "pl",
        "it",
        "tr",
        "zh",
        "ja",
        "ko",
    }
)

# Human-readable names for the scoring prompt
LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "ru": "Russian (Русский)",
    "uk": "Ukrainian (Українська)",
    "de": "German (Deutsch)",
    "fr": "French (Français)",
    "es": "Spanish (Español)",
    "pt": "Portuguese (Português)",
    "pl": "Polish (Polski)",
    "it": "Italian (Italiano)",
    "tr": "Turkish (Türkçe)",
    "zh": "Chinese (中文)",
    "ja": "Japanese (日本語)",
    "ko": "Korean (한국어)",
}


def normalize_analysis_language(code: str | None) -> str:
    if not code:
        return "en"
    c = code.strip().lower()
    return c if c in ALLOWED_ANALYSIS_LANGUAGES else "en"


def language_instruction_for_prompt(code: str) -> str:
    code = normalize_analysis_language(code)
    name = LANGUAGE_NAMES.get(code, "English")
    if code == "en":
        return (
            "Write all human-readable strings in the JSON response in English: short_feedback, "
            "every field inside detailed_feedback, each improvement_tip, and the correction values "
            "in spelling_errors. JSON keys must stay exactly as in the contract."
        )
    return (
        f"Write all human-readable strings in the JSON response in {name}: short_feedback, "
        "every field inside detailed_feedback, each improvement_tip, and the correction values "
        "in spelling_errors. The essay and task may be in English — still score using the rubric. "
        "JSON keys must stay exactly as in the contract (English key names)."
    )
