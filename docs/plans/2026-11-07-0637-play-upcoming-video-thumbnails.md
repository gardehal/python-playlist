# Fix Upcoming Video Layout and Add Thumbnails

## Problem

The upcoming QueueStreams section in `templates/play.html` uses the global Bootstrap `.row` class and renders each image beside its text through `.center`. The global CSS does not prevent Bootstrap's row from wrapping, and each link's content width varies with its title, producing inconsistent layouts. Every item currently uses `/static/default.png`.

YouTube thumbnails are not currently stored on `QueueStream`. The active YouTube fetch path is `FetchService.fetchYoutubeYdl`, which creates QueueStreams from yt-dlp playlist entries. `YoutubeProvider.fetch_metadata` also returns a `thumbnail`, but no thumbnail field currently exists on the model.

## Decisions

- D1: Implement the requested work in three phases: stabilize the existing default-image layout, add actual YouTube thumbnails, then extend thumbnail support to other sources.
- D2: Keep upcoming-list styling scoped to that section rather than changing the shared `.row` behavior across the site.
- D3: Make thumbnail data optional so existing QueueStream JSON records without a thumbnail remain usable and the UI can retain the default-image fallback.
- D4: For the first source integration, use the active `FetchService.fetchYoutubeYdl` path, which extracts flat playlist entries with yt-dlp. Verify whether those entries include a thumbnail before choosing extraction or fallback behavior; `YoutubeProvider.fetch_metadata` is not the active playlist-fetch path.

## Approach

1. In `templates/play.html` and `static/css/style.css`, give the upcoming list and each item dedicated classes. Display up to 16 upcoming items in a row-first grid of four fixed columns (four rows at the cap), including incomplete rows, with horizontal scrolling when four minimum-width columns do not fit. Stack the image and text within each item; constrain long text to the item width. Continue using the existing default image in this phase.
2. Add an optional thumbnail URL to `model/QueueStream.py`. Carry the URL from YouTube metadata through `FetchService.fetchYoutubeYdl` into stored QueueStreams, accounting for existing records without the field. Render the stored thumbnail in `play.html` and use `/static/default.png` when it is absent. Confirm the standard YouTube fetch-and-save flow persists and displays the URL.
3. Extend extraction and mapping for other implemented source types that provide usable thumbnails. Keep sources without thumbnail data on the default-image fallback, and avoid making thumbnail support a requirement for fetching or playing a stream.

## Todos

- [x] Phase 1: Add upcoming-list and item classes in `templates/play.html`; add a four-column, row-first grid with a 16-item cap, horizontal overflow handling, and constrained text in `static/css/style.css`.
- [x] Phase 1: User confirmed the fixed four-column grid behaves as expected across rows.
- [ ] Phase 1: Verify the no-upcoming state, long and short titles, and narrow and wide viewport widths; confirm the default image remains in use.
- [ ] Phase 2: Add an optional thumbnail URL field to `model/QueueStream.py` and verify the existing JSON persistence layer loads older records that omit it.
- [ ] Phase 2: Populate the field in the active YouTube fetch path in `services/FetchService.py`; verify the thumbnail value available from yt-dlp entries and retain a default fallback when absent.
- [ ] Phase 2: Render the thumbnail URL in `templates/play.html`, falling back to `/static/default.png`; verify a fetched YouTube QueueStream displays its thumbnail in the upcoming list.
- [ ] Phase 3: Identify thumbnail data for additional supported sources and map available values into QueueStream; retain the fallback for unsupported or missing thumbnails.
- [ ] Phase 3: Verify fetch, persistence, and upcoming-list rendering for each added source type without regressing streams that have no thumbnail.

## Validation

- User confirmed the fixed four-column grid behaves as expected across rows. The agent did not run the app; the no-upcoming state, long titles, and narrow viewport still need visual verification.
- Exercise the no-upcoming-items state and long-title layout.
- Verify existing QueueStream JSON records without thumbnail data still load and render the default image.
- Fetch a YouTube source through the normal application flow and verify a populated thumbnail is persisted and displayed.
- For phase three, repeat the fetch-and-render check for each added source type and confirm missing thumbnail values remain non-fatal.

## Results

- Phase 1: Replaced the shared Bootstrap row layout in `templates/play.html` with a dedicated grid, title/source text below each image, and the existing default-image fallback. Both `server.py` and `server_refactor.py` provide up to 16 upcoming streams; `static/css/style.css` places them in fixed four-column rows, including incomplete rows, with a 15rem minimum and horizontal scrolling on narrow screens. Titles remain constrained within their cards. The user confirmed the grid behaves as expected across rows.
- No app/browser validation was run by the agent; remaining visual edge checks are still open.
