# IELTS Writing Task 2 LLM Integration

## Goals

The LLM layer is responsible for:

- generating IELTS-style essay topics;
- scoring essays against IELTS criteria;
- returning structured, machine-validated responses;
- isolating provider-specific HTTP details from core application logic.

## Prompt Storage

Prompt templates must live outside service code.

Suggested structure:

- `backend/app/prompts/topic_generation/system.txt`
- `backend/app/prompts/essay_scoring/system.txt`
- `backend/app/prompts/shared/json_contract.txt`
- `backend/app/prompts/shared/ielts_rubric.txt`

## Provider Abstraction

### Base Client

`BaseLlmClient` defines:

- `generate_topic()`
- `score_essay()`

### Adapter

Each provider adapter:

- builds provider-specific request bodies;
- sends HTTP requests;
- extracts text or JSON from the provider response;
- normalizes provider errors.

### Factory

`LlmClientFactory` resolves the adapter by config:

- `yandex`
- future compatible providers

## Scoring Contract

The scoring response must be valid JSON matching a strict schema.

Required fields:

- `overall_band`
- `task_response_band`
- `coherence_band`
- `lexical_band`
- `grammar_band`
- `short_feedback`
- `detailed_feedback`
- `improvement_tips`

## Prompt Rules

The scoring system prompt should:

- define the assistant as an IELTS Writing Task 2 evaluator;
- embed or reference the IELTS rubric;
- require a JSON-only response;
- forbid surrounding prose;
- encourage concise but concrete feedback;
- avoid hallucinated certainty.

The topic generation prompt should:

- produce a realistic IELTS Writing Task 2 question;
- avoid duplicates if context is available;
- return plain prompt content only.

## Validation

Backend validation steps:

1. receive raw provider output;
2. parse JSON;
3. validate through Pydantic;
4. reject malformed responses;
5. retry if appropriate;
6. log failures with provider context.

## Error Strategy

- provider timeout -> return a retriable scoring error;
- malformed response -> retry once or more based on policy;
- authentication failure -> fail fast and log configuration issue;
- quota or rate limit -> return friendly user message and keep essay intact.

## Configuration

Expected environment variables:

- `LLM_PROVIDER`
- `LLM_API_KEY`
- `LLM_ENDPOINT`
- `LLM_MODEL`
- `LLM_TIMEOUT_SECONDS`

## Security Notes

- never expose provider keys to the frontend;
- never trust provider output without schema validation;
- avoid logging full essay text in production where possible.
