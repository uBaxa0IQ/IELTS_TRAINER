# IELTS Writing Task 2 Spellcheck Design

## Goal

Provide at least basic spelling highlighting in the writing editor without turning the editor into
a heavy document processor.

## Recommended First Implementation

Use browser-native spellcheck in the textarea-based editor.

Reasons:

- low complexity;
- good enough baseline for English spelling support;
- no backend dependency;
- no extra latency while typing;
- aligned with the product's minimalist design.

## UX Rules

- spellcheck should be enabled for English text input;
- writing must remain smooth even if spellcheck is imperfect;
- the UI should not overwhelm the user with intrusive markers;
- the app should explain that spelling hints are assistive, not part of IELTS scoring.

## Limitations

- browser behavior varies across environments;
- academic vocabulary may be flagged incorrectly;
- it does not replace grammar or coherence feedback;
- it may be weaker on long custom text than specialized writing tools.

## Fallback Behavior

If browser spellcheck is not available or disabled:

- editor still works normally;
- no server failure should occur;
- the user can still submit the essay;
- optional non-blocking helper text may explain reduced checking support.

## Future Upgrade Path

If a stronger solution is needed later:

- client-side language tool integration;
- backend spellcheck service;
- selective grammar assistance.

These upgrades are not required for the first release.
