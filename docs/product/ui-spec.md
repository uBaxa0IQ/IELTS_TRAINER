# IELTS Writing Task 2 UI Specification

## Design Direction

The interface should be visually minimal and performance-first.
The inspiration is `Monkeytype`: centered layout, muted contrast, strong typography, calm spacing,
and a focus on a single primary task.

## Visual Principles

- dark-first theme;
- low-noise layout with large empty space;
- clear hierarchy through type scale, not decorative chrome;
- restrained color palette;
- subtle highlight colors for active states and scores;
- minimal card usage;
- no heavy dashboard clutter on the writing screen.

## Primary Screens

### Landing

- concise value proposition;
- entry point to `Sign in`;
- short explanation of how the app works.

### Auth

- single-column auth form;
- Google sign-in button;
- inline validation errors.

### Practice Screen

The practice screen is the main product surface.

Expected sections:

- top bar with logo, navigation, and account access;
- topic panel;
- actions for generate topic and manual topic input;
- timer controls;
- editor area;
- word count and lightweight session status;
- primary submit button;
- score section rendered after evaluation.

Notes:

- logout is not shown on the practice screen;
- after a successful evaluation, the app preloads a new topic and clears the editor for the next attempt.

### History / Dashboard

- recent essays list;
- score trend chart;
- ability to open a previous attempt.

### Profile

- profile header with user identity and actions;
- direct link to `Settings`;
- logout action in profile context;
- dashboards section appears before history.

### Profile Settings

- dedicated route for user preferences;
- currently contains editable `nickname` and `Feedback language` selector;
- designed to be extended with additional settings later.

## Writing Screen Layout

### Top Bar

- product mark or logo on the left;
- account access on the right (nickname when signed in);
- no logout control in top bar.

### Topic Panel

- visible above the editor;
- readable line length;
- action buttons:
  - `Generate topic`
  - `Use my own topic`
  - `Replace topic`

### Timer Controls

- compact inline control;
- toggle to enable timer;
- duration selector;
- countdown display only when timer is active.

### Editor

- plain writing area with high readability;
- no toolbar or rich-text formatting controls;
- enough vertical space for long essays;
- spelling indications should not visually overpower the text.

### Footer Meta

- word count;
- timer state;
- save/evaluation status if relevant.

## Result Presentation

### Immediate Summary

Show first:

- overall band;
- 4 criterion bands;
- short feedback summary.

### Detailed Analysis

Hidden behind an explicit action such as `Show detailed analysis`.

The expanded panel may include:

- strengths;
- weaknesses;
- criterion-by-criterion explanation;
- suggested improvements;
- possible rewritten examples in future versions.

## States

Each primary area needs clear states.

### Topic Panel States

- no topic selected;
- generated topic loaded;
- manual topic loaded;
- topic loading;
- topic generation failed.

### Editor States

- empty;
- typing;
- spellcheck available;
- spellcheck degraded;
- timed session active;
- timed session expired;
- submitting;
- evaluation failed.

### Score States

- not evaluated yet;
- evaluating;
- summary available;
- detailed analysis expanded;
- evaluation failed.

## Responsiveness

- desktop first;
- tablet supported without losing writing comfort;
- mobile can support review and light writing, but the long-form experience is optimized for larger screens.

## Accessibility

- keyboard-first navigation;
- sufficient contrast;
- focus states on all interactive controls;
- readable font sizing;
- status messages must not rely on color alone.
