# Improve Playlist Fetch and Navigation

## Problem

Fetching a playlist currently starts a daemon thread in `server.py` and redirects back to the page. The playlist details template calls the route through `fetch()` but ignores its response, so the QueueStream rows and counts stay stale until a manual reload. Flask flash messages are rendered only during a page request; the background worker cannot reliably flash completion or error messages into the browser.

The shared layout displays server-rendered flash toasts, but has no client-side helper for fetch results. Replacing QueueStream rows also risks losing their watched-toggle listeners; the current toggle response does not return the `watched` value expected by the page.

Several successful create and edit POST handlers call another view directly instead of redirecting. For example, YouTube playlist creation renders playlist details while the browser remains on the creation URL. Subsequent actions using `request.referrer` can therefore return to a create form instead of the displayed details page; refresh may also resubmit the POST. Confirmation-page cancel links likewise rely on the referrer.

## Decisions

- D1: Keep Flask, Jinja, and the existing server-rendered page flow; do not replace the frontend architecture.
- D2: Scope dynamic updates to playlist fetch. Also correct the affected playlist-related create/edit/delete navigation using post/redirect/get; retain normal server-rendered forms and flash messages.
- D3: Use a JSON start/status API with browser polling rather than WebSockets or server-sent events. Fetch already runs in a background thread, and polling needs no new infrastructure.
- D4: Keep task state in process memory for this local single-process application. Capture worker errors in task status rather than calling `flash()` from the worker; expire completed task entries to avoid unbounded growth.
- D5: Target `server.py`, the active server used for manual verification. Do not broaden this task to `server_refactor.py` unless it becomes an active entrypoint.
- D6: Use explicit local landing routes after successful actions and for confirmation cancellation; do not blindly redirect to an unvalidated referrer. Failed validation stays on the form with its errors.
- D7: Keep fetch controls usable and feedback visible during pending, completed, failed, and network-error states. Avoid duplicate fetches for the same playlist while one is active.

## Approach

1. Add lock-protected in-memory fetch task state in `server.py` with pending/running/completed/failed status, a result count, and safe error text. Provide a CSRF-protected POST start endpoint and a JSON status endpoint; return an accepted task ID promptly and define responses for missing playlists, duplicate starts, and unknown or expired tasks.
2. Run the existing fetch operation in the background, store its result or failure without request-context flashes, and expire terminal entries with bounded cleanup. Preserve the active operation when another start is attempted.
3. Keep fetch monitoring in the shared layout. Store active task IDs in tab-scoped `sessionStorage`, resume polling on each page load, keep the spinner open until a terminal result, and then show a separate result toast. Anchor the toast container to the viewport.
4. Extract the QueueStreams table and count into a reusable Jinja partial or a targeted response. Refresh that section after success without a full reload, preserve links and playback indices, and use event delegation or rebind watched-toggle handlers. Return the actual watched state from the toggle endpoint so the row updates correctly.
5. Add a small client-side toast mechanism that inserts message text safely and preserves existing server-rendered flash toasts.
6. Replace direct success-view calls in affected playlist, QueueStream, and StreamSource create/edit/delete flows with redirects to an appropriate details or index URL. Use explicit local cancel destinations on confirmation pages and remove referrer dependence from affected playlist actions; keep validation errors on the form.
7. Add focused server and browser-level tests for task lifecycle, partial refresh and watched toggles, navigation, flash messages, and errors.

## Todos

- [x] Add in-memory fetch task state and JSON start/status endpoints in `server.py`.
- [x] Capture background fetch success and exceptions in task status; do not call `flash()` from the worker.
- [x] Update Fetch new to show start, completion/result, failure, and prolonged status-network-error toasts; prevent duplicate starts and restore the control.
- [ ] Refresh the QueueStreams section and count after successful fetch without reloading; retain working watched controls and correct row state.
- [ ] Redirect affected successful form submissions and confirmation cancels to explicit appropriate landing pages.
- [ ] Add focused tests for task lifecycle, duplicate starts, failure/recovery, refreshed controls, and post/redirect/get navigation.
- [ ] Verify ordinary Flask flash messages, validation errors, and non-fetch page navigation still work.

## Notes / considerations

- In-memory task state is appropriate only while the app runs as a single process. Multiple worker processes or durable job recovery would require shared storage and are out of scope.
- Keep the polling interval and task cleanup policy modest; the exact values are TBD during implementation.
- Fetch partials must not consume unrelated flashed messages, and client-generated toast content must be inserted as text rather than HTML.
- Keep user-provided return URLs out of redirects unless validated as local; prefer known route destinations.
- Making every page action dynamic is a separate project; only the affected navigation flows are included here.

## Validation

- Verify fetch starts without navigation and returns a task identifier.
- Verify pending status is observable while a mocked/slow fetch runs, then completed status refreshes the QueueStreams and count.
- Verify worker exceptions result in an error toast without relying on Flask request context.
- Verify repeated starts do not launch duplicate work, polling stops after terminal or unrecoverable errors, the control recovers, and task state is eventually cleaned up.
- Verify refreshed rows retain correct playback links and watched toggles, including the displayed watched state.
- Verify create/edit/delete successes redirect to the appropriate GET page, cancellation returns to a sensible local page, and refresh does not resubmit forms.
- Verify standard flash messages, invalid-form errors, and server-rendered navigation remain intact.

## Results

- First vertical slice implemented: `POST /fetch/<playlistId>` returns a task ID, while `GET /fetch/tasks/<taskId>` reports pending/running/completed/failed status and the number of new QueueStreams.
- Fetch tasks are deduplicated per playlist, terminal task records expire after five minutes, and worker errors are logged and surfaced through status rather than Flask flash state.
- The shared layout stores active fetch IDs in `sessionStorage` and resumes polling silently after same-tab navigation or reload. Only the page that starts a fetch shows its spinner; resumed status checks run every three seconds (backing off to five seconds after repeated failures). Completion/error appears as a separate toast that stays until dismissed, and all toasts are fixed to the viewport's top-right corner.
- Focused server/use-case and details-template tests passed; `python -m unittest discover -s tests -p "test*.py" -q` passed 85 tests. `compileall` for changed Python files and `git diff --check` also passed.
