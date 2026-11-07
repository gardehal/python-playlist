# Update Playlist Details After Fetch

## Problem

Fetching a playlist currently starts a daemon thread in `server.py` and redirects back to the page. The playlist details template calls the route through `fetch()` but ignores its response, so the QueueStream rows and counts stay stale until a manual reload. Flask flash messages are rendered only during a page request; the background worker cannot reliably flash completion or error messages into the browser.

The shared layout has a `showFlashedToasts()` helper, but the fetch flow does not call it and it expects an element ID that the layout does not currently define.

## Decisions

- D1: Keep Flask, Jinja, and the existing server-rendered page flow; do not replace the frontend architecture.
- D2: Scope this task to asynchronous fetch from playlist details. Other forms and normal post/redirect/get flashes remain unchanged.
- D3: Use a JSON start/status API with browser polling rather than WebSockets or server-sent events. Fetch already runs in a background thread, and polling needs no new infrastructure.
- D4: Keep task state in process memory for this local single-process application. Capture worker errors in task status rather than calling `flash()` from the worker; expire completed task entries to avoid unbounded growth.
- D5: Target `server.py`, the active server used for manual verification. Do not broaden this task to `server_refactor.py` unless it becomes an active entrypoint.

## Approach

1. Add fetch task state in `server.py` with explicit pending/running/completed/failed status, result summary, and error text. Add a JSON endpoint to start a fetch and another to read its status.
2. Return an accepted response and task ID immediately from the start endpoint. Run the existing fetch operation in the background and store its terminal result or exception in task state.
3. Update the Fetch new action in `templates/playlists/details.html` to start the task, poll its status at a modest interval, stop polling on completion/failure, and display a Bootstrap toast from the returned result.
4. Extract the QueueStreams table and count into a reusable Jinja partial or add a targeted JSON endpoint. After successful fetch, refresh only that details section and its count without reloading the document.
5. Fix or replace the unused client-side toast helper only as needed for this fetch workflow; preserve current server-rendered toast behavior for regular navigation.
6. Add focused tests for task start, completion, failure, and updated playlist details response using a mocked fetch operation.

## Todos

- [ ] Add in-memory fetch task state and JSON start/status endpoints in `server.py`.
- [ ] Capture background fetch success and exceptions in task status; do not call `flash()` from the worker.
- [ ] Update the Fetch new control in `templates/playlists/details.html` to poll and show completion/failure toasts.
- [ ] Refresh the QueueStreams section and count after successful fetch without reloading the full page.
- [ ] Add focused tests for pending, completed, failed, and updated-details behavior.
- [ ] Verify ordinary Flask flash messages and non-fetch page navigation still work unchanged.

## Notes / considerations

- In-memory task state is appropriate only while the app runs as a single process. Multiple worker processes or durable job recovery would require shared storage and are out of scope.
- Keep the polling interval and task cleanup policy modest; the exact values are TBD during implementation.
- This is a small-to-medium scoped change, not a Flask or frontend replacement. Making every page action dynamic is a separate project.

## Validation

- Verify fetch starts without navigation and returns a task identifier.
- Verify pending status is observable while a mocked/slow fetch runs, then completed status refreshes the QueueStreams and count.
- Verify worker exceptions result in an error toast without relying on Flask request context.
- Verify polling stops after a terminal state and task state is eventually cleaned up.
- Verify standard flash messages and server-rendered page navigation remain intact.

## Results
