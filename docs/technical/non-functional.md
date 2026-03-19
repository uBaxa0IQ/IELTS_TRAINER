# IELTS Writing Task 2 Non-Functional Requirements

## Performance

- practice screen should feel responsive on first interaction;
- word count updates should be effectively instant for normal essay sizes;
- score requests may take longer, but loading states must remain clear;
- chart rendering should stay lightweight.

## Reliability

- user text must not be lost on transient scoring errors;
- LLM failures must not corrupt stored submissions;
- backend should validate all external responses before persistence.

## Security

- passwords must be hashed securely;
- JWT secrets must come from environment variables;
- provider API keys must remain server-side only;
- protected routes must require valid auth tokens.

## Privacy

- essay text is user data and should be treated as sensitive content;
- logs should avoid storing full essay bodies in normal operation;
- API errors exposed to the client should remain generic.

## Observability

- backend should log scoring failures, provider errors, and auth failures;
- request IDs are useful for tracing;
- future metrics may include scoring latency and provider error rate.

## Maintainability

- prompt templates must be stored separately from service logic;
- LLM provider integrations must remain swappable;
- API contracts should be explicit and typed;
- code should prefer simple modules over speculative abstractions.

## Testing

Minimum test coverage should include:

- auth success and failure cases;
- prompt generation endpoints;
- essay evaluation request validation;
- LLM response schema validation;
- protected route behavior;
- analytics endpoint shape.

## Rate Limiting

- auth endpoints should be rate limited if exposed publicly;
- scoring and generation endpoints should have basic abuse protection;
- repeated LLM retries should be bounded.
