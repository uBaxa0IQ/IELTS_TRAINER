# IELTS Writing Task 2 Editor Specification

## Purpose

The editor is the core interaction area of the product.
It must stay minimal, stable, and optimized for focused writing rather than rich formatting.

## Responsibilities

- display the active essay topic;
- allow manual topic input;
- capture essay text;
- count words in real time;
- support optional timed practice;
- provide basic spelling feedback;
- submit the final essay for evaluation.

## Topic Modes

The editor supports three topic modes:

- `preset`: chosen from a local topic pool;
- `generated`: returned from the LLM topic generation flow;
- `manual`: entered or pasted by the user.

The active topic must remain visible while writing.

## Manual Topic Input

Requirements:

- user can open a compact input panel or modal;
- user can paste or type a custom IELTS-style topic;
- empty input must be rejected;
- topic source must be stored as `manual`;
- switching topics should require confirmation if the essay already has content.

## Essay Input

- text is entered as plain text;
- no formatting toolbar;
- line wrapping and comfortable reading width;
- cursor behavior should remain native;
- clipboard paste must be supported.

## Word Count

- count updates on each text change;
- words should be counted using a predictable plain-text rule;
- the current count must remain visible during writing;
- low word count warnings may appear below expected IELTS length.

## Timer

Timer requirements:

- optional toggle to enable or disable timer;
- selectable duration before or at session start;
- countdown visible during timed sessions;
- when the timer expires, the UI must indicate timeout clearly;
- essay content must not be lost at timeout;
- submission after timeout is still allowed in the default rules.

Recommended preset durations:

- `20 min`
- `30 min`
- `40 min`
- `60 min`

## Spelling Highlighting

The editor must provide at least basic spelling support for English text.

Requirements:

- highlight likely spelling issues;
- do not block typing;
- do not auto-correct silently;
- degrade gracefully if the spellcheck mechanism is unavailable;
- avoid heavy visual noise.

Preferred first implementation:

- browser-native spellcheck plus clear UX messaging;
- optional future upgrade to more advanced checking if needed.

## Submission Rules

The submit action should validate:

- user is authenticated;
- topic is present;
- essay text is not empty;
- frontend is not already submitting.

Warnings are allowed for:

- unusually low word count;
- expired timer;
- possible incomplete essay.

## Draft and Session Behavior

The documentation and implementation should support a draft-friendly flow.

Minimum behavior:

- local preservation of in-progress text during the current session;
- no accidental loss when score request fails;
- safe topic switching prompts if essay text exists.

## Error States

- missing topic;
- empty essay;
- topic generation failed;
- score request failed;
- spellcheck unavailable;
- timer expired;
- network interruption.

## Non-Goals

- rich text formatting;
- collaborative editing;
- grammar rewriting inside the editor;
- intrusive AI suggestions during composition.
