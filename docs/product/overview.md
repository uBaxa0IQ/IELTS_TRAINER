# IELTS Writing Task 2 Product Overview

## Product Vision

The product is a minimalist web application for deliberate practice of `IELTS Writing Task 2`.
It should feel fast, calm, and distraction-free, similar in spirit to `Monkeytype`, while still
providing enough structure for serious exam preparation.

The application helps a learner:

- get a writing topic quickly;
- write an essay in a clean editor;
- track time and word count;
- receive an IELTS-style score with actionable feedback;
- review previous attempts and score trends over time.

## Target Audience

- learners preparing for `IELTS Academic` or `IELTS General Training`;
- users who want repeated writing practice without a full LMS;
- self-study users who need quick scoring and progress tracking;
- teachers or tutors who may later reuse the platform with students.

## Product Principles

- minimal interface with low visual noise;
- fast interaction, no unnecessary setup before writing;
- documentation-first and contract-driven development;
- clear separation between writing, scoring, and history;
- transparent feedback instead of opaque "AI magic";
- easy replacement of LLM provider without rewriting business logic.

## Core User Jobs

1. Start a writing session in seconds.
2. Get or enter a valid essay topic.
3. Write with time awareness and spelling assistance.
4. Submit the essay for IELTS-style evaluation.
5. Understand both the score and the reasons behind it.
6. Revisit old essays and see progress over time.

## Full Product Scope

The first full release includes:

- account registration and login;
- authenticated personal workspace;
- topic generation through LLM API;
- manual topic input by the user;
- local fallback topics stored by the application;
- writing editor with live word count;
- optional timer with custom duration;
- basic spelling highlighting for English text;
- essay submission and server-side evaluation;
- IELTS scoring by four criteria and overall band;
- short summary plus expanded detailed analysis;
- automatic next-topic refresh and editor clear after successful evaluation;
- profile page with dashboards first and history below;
- dedicated profile settings page for feedback language;
- essay history with attempt details;
- score trend chart in the user dashboard.

## Explicitly Out of Scope

The following are intentionally not part of this release:

- social features;
- tutor or admin panel;
- collaborative editing;
- peer review workflows;
- multi-task IELTS modules outside `Writing Task 2`;
- force-fitting enterprise architecture patterns where simple modules are enough.

## Roles

### Guest

- can view landing and auth pages;
- cannot save essays or view analytics;
- may be allowed to preview the practice interface, but not persist data.

### Authenticated User

- can create writing sessions;
- can generate or manually enter topics;
- can write, submit, and review essays;
- can access full history and analytics.

## Success Criteria

The release is successful if a new user can:

1. sign in with Google;
2. start a writing session in under 30 seconds;
3. submit an essay and receive structured feedback;
4. revisit past results without losing work;
5. observe score changes over time in the dashboard.

## Functional Requirements Summary

- the system must support Google OAuth authentication;
- the system must let the user generate or manually enter a topic;
- the system must count words in real time;
- the system must support an optional countdown timer with user-defined duration;
- the system must highlight basic spelling mistakes in English;
- the system must evaluate essays through an LLM provider using a structured contract;
- the system must store essays, scores, and analysis;
- the system must display score history and trend data per user.

## Constraints

- frontend stack: `React + TypeScript`;
- backend stack: `FastAPI`;
- database: `PostgreSQL`;
- LLM integration should support `Yandex Cloud` or compatible provider flows;
- prompt templates must be stored separately from service logic;
- the UI should remain minimal and not become a heavy rich-text editor.
