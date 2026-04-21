# IELTS Writing Trainer

Full-stack training app for `IELTS Writing Task 2`.

## Stack

- `React + TypeScript + Vite`
- `FastAPI`
- `PostgreSQL`
- `Recharts`
- `Adapter + Factory` pattern for LLM providers

## Features

- email/password authentication;
- generated topics and manual topic input;
- minimalist writing interface;
- word count;
- optional timer with duration presets;
- browser-based spelling support;
- IELTS-style score summary and detailed analysis;
- automatic next-topic preload and editor reset after successful evaluation;
- profile workspace with dashboards and history;
- dedicated profile settings page for feedback language.

## Docs

Project documentation lives in `docs/`.

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment

Copy `.env.example` to `.env` and update values as needed.

Default `LLM_PROVIDER=mock` lets the app run without an external model key.

To switch to a real provider, configure:

- `LLM_PROVIDER=yandex`
- `LLM_API_KEY`
- `LLM_ENDPOINT`
- `LLM_MODEL`

## Docker

```bash
docker compose up --build
```

For day-to-day development, run once with build and then use plain:

```bash
docker compose up
```

`docker-compose.yml` is configured for live reload:

- backend runs `uvicorn ... --reload` with source volume mount;
- frontend runs Vite dev server with mounted source and polling for file watching on Windows.

This means most code changes are reflected without rebuilding or restarting the full stack.
