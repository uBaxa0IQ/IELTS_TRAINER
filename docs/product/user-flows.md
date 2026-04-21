# IELTS Writing Task 2 User Flows

## Main Flow: Authenticated Writing Session

1. User signs in.
2. User lands on the practice screen.
3. System displays a topic or lets the user create one.
4. User optionally enables the timer and chooses duration.
5. User writes the essay while seeing word count and spelling hints.
6. User submits the essay for evaluation.
7. System validates the request and sends it to the scoring pipeline.
8. User receives the overall band, criterion bands, and short feedback.
9. User can expand the full analysis.
10. System saves the session in history and updates analytics.
11. Frontend preloads a new topic and clears the editor for the next attempt.

## Flow: Sign Up

1. Guest opens the auth page.
2. Guest enters email and password.
3. System validates credentials format and uniqueness.
4. System creates the user account and returns tokens.
5. User is redirected to the practice screen.

## Flow: Sign In

1. Existing user opens the auth page.
2. User enters email and password.
3. System validates credentials.
4. System returns access and refresh tokens.
5. User is redirected to the last relevant screen.

## Flow: Generate Topic

1. User opens the practice screen.
2. User clicks `Generate topic` or `Generate another topic`.
3. Frontend requests a topic from backend.
4. Backend uses fallback topic storage or LLM topic generation.
5. Topic appears in the topic panel.
6. User starts writing immediately.

## Flow: Manual Topic Input

1. User opens the practice screen.
2. User clicks `Use my own topic`.
3. User pastes or types the essay prompt.
4. Frontend validates that the topic is not empty.
5. Topic becomes the active session prompt with source `manual`.

## Flow: Timer Setup

1. User toggles `Enable timer`.
2. User selects a duration, for example `20`, `30`, `40`, or `60` minutes.
3. Timer starts when the session begins or when writing starts.
4. Frontend shows live countdown.
5. When time expires, the user is informed and the session is marked as timed out.
6. The product should define whether editing remains possible after timeout; default behavior is to allow submission but visually mark the session as over time.

## Flow: Essay Submission and Scoring

1. User clicks `Evaluate essay`.
2. Frontend checks basic conditions:
   - topic exists;
   - essay is not empty;
   - user is authenticated.
3. Backend stores or prepares the submission.
4. Backend sends essay and topic into the scoring service.
5. Scoring service loads prompt template and requests a structured LLM response.
6. Backend validates JSON response.
7. Backend stores score and analysis.
8. Frontend displays summary cards first.
9. User can open the detailed analysis panel.

## Flow: View History

1. User opens the dashboard or history page.
2. Frontend requests the user's previous submissions.
3. Backend returns paginated history.
4. User sees date, topic preview, overall band, and score breakdown.
5. User opens an item to review details.

## Flow: Profile and Settings

1. Authenticated user opens profile.
2. Profile shows dashboards first, then history list.
3. User can open `Settings` from profile.
4. In settings, user changes `feedback language`.
5. Frontend sends `PATCH /auth/me` and updates local auth user state.
6. User returns to profile and continues practice with updated preference.
7. Logout is triggered from profile (not from practice top bar).

## Flow: View Progress Analytics

1. User opens the dashboard analytics area.
2. Frontend requests score trend data.
3. Backend returns chart-ready points by submission date.
4. User sees a simple trend chart and can compare recent progress.

## Error and Edge Flows

### Empty Topic

- prevent submission;
- show a clear inline error;
- offer generation or manual input action.

### Empty or Too Short Essay

- prevent evaluation if the essay is empty;
- warn the user if the word count is far below IELTS expectations.

### LLM Failure

- show non-destructive error state;
- keep the essay text intact;
- allow retry without data loss.

### Invalid LLM JSON

- backend retries if configured;
- if still invalid, backend logs the event and returns a safe failure message.

### Spelling Service Unavailable

- writing must still work;
- spellcheck feature degrades gracefully;
- no user data should be lost.

### Timer Expiry

- visual state changes to indicate timeout;
- session can still be reviewed and submitted unless product rules later change.
