# IELTS Writing Task 2 Data Model

## Overview

The application needs persistent storage for:

- users;
- prompts;
- essay submissions;
- optional refresh tokens or session tracking if implemented;
- analytics derived from submissions.

## Core Tables

### users

Purpose: store account identity.

Fields:

- `id` UUID primary key
- `email` unique, indexed
- `password_hash` (nullable for Google accounts)
- `nickname` (display name, editable)
- `google_sub` (stable Google account identifier, nullable)
- `analysis_language` string (BCP-47-style code, default `en`) — language for LLM-written feedback text
- `created_at`
- `updated_at`

### analytics_events

Purpose: minimal, privacy-preserving tracking for product usage analytics.

Fields:

- `id` UUID primary key
- `user_id` foreign key to `users.id`
- `event_type` string (e.g. `signup_google`, `login_google`, `topic_generated`, `essay_evaluated`)
- `meta` JSON (lightweight metadata; no essay text)
- `created_at`

### essay_prompts

Purpose: store topic content and its source.

Fields:

- `id` UUID primary key
- `topic_text`
- `source` enum: `preset`, `generated`, `manual`
- `tags` JSON or array, nullable
- `created_by_user_id` nullable foreign key for manual topics if needed
- `created_at`

### essay_submissions

Purpose: store submitted essays and evaluation results.

Fields:

- `id` UUID primary key
- `user_id` foreign key
- `prompt_id` foreign key
- `essay_text`
- `word_count`
- `timer_enabled`
- `timer_duration_seconds` nullable
- `timer_expired`
- `task_response_band`
- `coherence_band`
- `lexical_band`
- `grammar_band`
- `overall_band`
- `short_feedback`
- `analysis_json`
- `status` enum: `pending`, `scored`, `failed`
- `failure_reason` nullable
- `created_at`
- `updated_at`

## Relationships

- one `user` has many `essay_submissions`;
- one `essay_prompt` can be referenced by many `essay_submissions`;
- one manual prompt may optionally belong to a specific `user`.

## Indexing

Recommended indexes:

- `users.email` unique index;
- `essay_submissions.user_id`;
- `essay_submissions.created_at`;
- `essay_submissions.user_id + created_at`;
- `essay_prompts.source`.

## History and Analytics

The initial analytics can be derived directly from `essay_submissions`.
No separate analytics table is required in the first version.

Chart data can be built from:

- submission date;
- overall band;
- optionally per-criterion bands.

## Draft Handling

The first implementation may keep drafts client-side instead of in the database.
If server-side drafts become necessary later, add a `writing_sessions` table.

## Notes

- `analysis_json` should preserve the full validated model response;
- numeric band values should support halves, for example `6.5`;
- keep schema flexible enough for future feedback extensions without immediate over-normalization.
