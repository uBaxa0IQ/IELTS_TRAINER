# IELTS Writing Task 2 API Contract

## Auth

### `POST /api/v1/auth/register`

Disabled: email/password registration is not supported. Use Google OAuth.

### `POST /api/v1/auth/login`

Disabled: email/password login is not supported. Use Google OAuth.

### `GET /api/v1/auth/google/login`

Starts Google OAuth sign-in by redirecting the browser to Google.

### `GET /api/v1/auth/google/callback`

Google redirects back here with an authorization `code`. The backend exchanges the code, validates the `id_token`, upserts the user, issues JWTs, and redirects the browser back to the frontend with `?token=<access_token>`.

### `GET /api/v1/auth/me`

Returns authenticated user profile (includes `analysis_language`, default `en`, and `nickname`).

### `PATCH /api/v1/auth/me`

Update preferences. Request body (all fields optional):

```json
{
  "analysis_language": "ru",
  "nickname": "alex"
}
```

Allowed codes match backend whitelist (e.g. `en`, `ru`, `uk`, `de`, …). Response: updated `UserRead`.

Frontend note: this endpoint is currently managed from the dedicated profile settings screen (`/profile/settings`).

## Prompts

### `POST /api/v1/prompts/generate`

Request:

```json
{
  "mode": "generated"
}
```

Response:

```json
{
  "id": "uuid",
  "topic_text": "Some IELTS Task 2 prompt",
  "source": "generated"
}
```

### `POST /api/v1/prompts/manual`

Request:

```json
{
  "topic_text": "Some IELTS Task 2 prompt typed by the user"
}
```

Response:

```json
{
  "id": "uuid",
  "topic_text": "Some IELTS Task 2 prompt typed by the user",
  "source": "manual"
}
```

## Essays

### `POST /api/v1/essays/evaluate`

Request:

```json
{
  "prompt_id": "uuid",
  "essay_text": "Essay body...",
  "timer_enabled": true,
  "timer_duration_seconds": 2400,
  "timer_expired": false
}
```

Response:

```json
{
  "submission_id": "uuid",
  "word_count": 287,
  "overall_band": 6.5,
  "task_response_band": 6.5,
  "coherence_band": 6.0,
  "lexical_band": 7.0,
  "grammar_band": 6.0,
  "short_feedback": "Clear position, but development is uneven in body paragraphs.",
  "detailed_feedback": {
    "task_response": "Detailed explanation...",
    "coherence_and_cohesion": "Detailed explanation...",
    "lexical_resource": "Detailed explanation...",
    "grammatical_range_and_accuracy": "Detailed explanation..."
  },
  "improvement_tips": [
    "Add more specific support for the second main point."
  ]
}
```

### `GET /api/v1/essays`

Returns paginated submission history for the current user.

Query params:

- `page`
- `page_size`

### `GET /api/v1/essays/{submission_id}`

Returns the full details of a single submission.

## Analytics

### `GET /api/v1/analytics/progress`

Response:

```json
{
  "points": [
    {
      "submission_id": "uuid",
      "created_at": "2026-03-19T10:00:00Z",
      "overall_band": 6.5
    }
  ]
}
```

### `POST /api/v1/analytics/events`

Logs lightweight analytics events for the currently authenticated user.

Request:

```json
{
  "event_type": "signup_google | login_google | topic_generated | essay_evaluated",
  "meta": {
    "any": "lightweight, no essay text"
  }
}
```

Response:

```json
{
  "ok": "true"
}
```

## Error Contract

All error responses should follow a predictable format:

```json
{
  "detail": {
    "code": "SCORING_FAILED",
    "message": "Unable to score essay right now."
  }
}
```

## Auth Rules

- `register` and `login` are disabled (email/password auth не поддерживается);
- Google OAuth endpoints are available when `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are configured;
- `me`, `prompts/manual`, `essays`, and `analytics` require auth;
- `prompts/generate` may be public or protected, but protected is preferred for consistency.
