# IELTS Writing Task 2 Implementation Roadmap

## Phase 1: Foundations

- scaffold `FastAPI` backend;
- scaffold `React + TypeScript` frontend;
- set up `PostgreSQL` integration;
- add environment-based configuration;
- prepare containerized local development.

## Phase 2: Authentication and Data

- implement registration and login;
- implement JWT auth;
- define database models and migrations;
- create persistence for prompts and submissions.

## Phase 3: Writing Experience

- build practice page;
- add topic generation and manual topic input;
- add word count;
- add timer controls and countdown;
- enable basic spellcheck.
- after successful evaluation, auto-load a new topic and clear editor draft.

## Phase 4: Scoring

- implement prompt loading;
- implement LLM adapter and factory;
- validate structured scoring responses;
- persist full scoring results.

## Phase 5: Review and Analytics

- build profile page with dashboards first;
- move preferences into dedicated profile settings page;
- place logout action in profile context;
- build history section under dashboards;
- build submission detail view;
- build progress chart from submission history.

## Phase 6: Hardening

- add tests;
- improve error handling;
- polish UX states;
- finalize README and local run instructions.
