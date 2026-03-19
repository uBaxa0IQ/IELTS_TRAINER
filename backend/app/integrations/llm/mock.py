from app.integrations.llm.base import BaseLlmClient
from app.schemas.llm import DetailedFeedback, EssayScoreResult, SpellingError


class MockLlmClient(BaseLlmClient):
    def generate_topic(self, *, topic_constraints: str | None = None) -> str:
        return (
            "Some people believe that university education should be free for everyone. "
            "To what extent do you agree or disagree?"
        )

    def score_essay(self, topic: str, essay_text: str, *, language: str = "en") -> EssayScoreResult:
        word_count = len([word for word in essay_text.split() if word.strip()])
        base_score = 5.5
        if word_count >= 220:
            base_score = 6.0
        if word_count >= 260:
            base_score = 6.5
        if word_count >= 320:
            base_score = 7.0

        if language.lower().startswith("ru"):
            return EssayScoreResult(
                overall_band=base_score,
                task_response_band=base_score,
                coherence_band=max(5.0, base_score - 0.5),
                lexical_band=min(7.5, base_score + 0.5),
                grammar_band=max(5.0, base_score - 0.5),
                short_feedback="Позиция ясная, но примеры и развитие абзацев можно усилить.",
                detailed_feedback=DetailedFeedback(
                    task_response="Эссе отвечает на задание, но идеи местами стоит раскрыть конкретнее.",
                    coherence_and_cohesion="Абзацы в целом логичны; переходы между мыслями можно сделать плавнее.",
                    lexical_resource="Лексики достаточно для задачи, но разнообразие усилит ответ.",
                    grammatical_range_and_accuracy="В целом предложения понятны; больше вариативности и меньше мелких ошибок поднимут балл.",
                ),
                improvement_tips=[
                    "Подкрепляйте каждый тезис конкретным примером.",
                    "Добавьте чёткие тематические предложения в абзацах.",
                    "Варьируйте структуры предложений, сохраняя точность.",
                ],
                spelling_errors=[
                    SpellingError(word="goverment", correction="government"),
                    SpellingError(word="educaton", correction="education"),
                ],
            )

        return EssayScoreResult(
            overall_band=base_score,
            task_response_band=base_score,
            coherence_band=max(5.0, base_score - 0.5),
            lexical_band=min(7.5, base_score + 0.5),
            grammar_band=max(5.0, base_score - 0.5),
            short_feedback="Clear overall position with room for more precise support and tighter paragraph development.",
            detailed_feedback=DetailedFeedback(
                task_response="The essay addresses the topic and presents a position, but some ideas could be expanded with more specific examples.",
                coherence_and_cohesion="Paragraphing is generally logical, though transitions and progression between ideas can be more controlled.",
                lexical_resource="Vocabulary is sufficient for the task, with some good topic-specific choices, but greater variety would strengthen the response.",
                grammatical_range_and_accuracy="Sentence control is mostly clear, although more varied structures and fewer small errors would improve the band.",
            ),
            improvement_tips=[
                "Support each main point with a more concrete example.",
                "Use clearer topic sentences for body paragraphs.",
                "Vary sentence structures while keeping accuracy high.",
            ],
            spelling_errors=[
                SpellingError(word="goverment", correction="government"),
                SpellingError(word="educaton", correction="education"),
            ],
        )
