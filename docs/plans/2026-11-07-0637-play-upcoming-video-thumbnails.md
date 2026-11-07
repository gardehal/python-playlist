# Fix Upcoming Video Layout and Add Thumbnails

## Problem

The upcoming QueueStreams section in `templates/play.html` uses the global Bootstrap `.row` class and renders each image beside its text through `.center`. The global CSS does not prevent Bootstrap's row from wrapping, and each link's content width varies with its title, producing inconsistent layouts. Every item currently uses `/static/default.png`.

YouTube thumbnails are not currently stored on `QueueStream`. The active YouTube fetch path is `FetchService.fetchYoutubeYdl`, which creates QueueStreams from yt-dlp playlist entries. `YoutubeProvider.fetch_metadata` also returns a `thumbnail`, but no thumbnail field currently exists on the model.

## Decisions

- D1: Implement the requested work in three phases: stabilize the existing default-image layout, add actual YouTube thumbnails, then extend thumbnail support to other sources.
- D2: Keep upcoming-list styling scoped to that section rather than changing the shared `.row` behavior across the site.
- D3: Make thumbnail data optional. For existing YouTube records, derive the standard thumbnail URL from `remoteId` when the record URI has a YouTube host; records from other sources retain the default-image fallback.
- D4: For the first source integration, use the active `FetchService.fetchYoutubeYdl` path, which extracts flat playlist entries with yt-dlp. Prefer each entry's `thumbnail`; fall back to YouTube's `hqdefault` image URL built from the video ID. `YoutubeProvider.fetch_metadata` is not the active playlist-fetch path.
- D5: Reuse `QueueStream.thumbnailUrl` and the existing browser `<img>` rendering for other sources. Prefer a usable source-provided image URL; download the image only if direct loading is unavailable or proves unreliable.
- D6: Do not backfill thumbnails for previously fetched Odysee QueueStreams in this task. Those records retain the default image; newly fetched Odysee streams get their per-item RSS thumbnail.

## Approach

1. In `templates/play.html` and `static/css/style.css`, give the upcoming list and each item dedicated classes. Display up to 16 upcoming items in a row-first grid of four fixed columns (four rows at the cap), including incomplete rows, with horizontal scrolling when four minimum-width columns do not fit. Stack the image and text within each item; constrain long text to the item width. Continue using the existing default image in this phase.
2. Add an optional thumbnail URL to `model/QueueStream.py`. Carry the URL from YouTube metadata through `FetchService.fetchYoutubeYdl` into stored QueueStreams, and derive it from `remoteId` for existing YouTube records without the field. Render the stored thumbnail in `play.html` and use `/static/default.png` when it is absent. Confirm the standard YouTube fetch-and-save flow persists and displays the URL.
3. Extend Odysee extraction by identifying its RSS item thumbnail metadata and passing a usable source URL into `QueueStream.thumbnailUrl`. Keep existing Odysee items without stored URLs and new items without usable metadata on the default-image fallback; do not backfill or download images. Rumble is deferred because its fetch implementation is incomplete.

## Todos

- [x] Phase 1: Add upcoming-list and item classes in `templates/play.html`; add a four-column, row-first grid with a 16-item cap, horizontal overflow handling, and constrained text in `static/css/style.css`.
- [x] Phase 1: User confirmed the fixed four-column grid behaves as expected across rows.
- [x] Phase 1: User confirmed the last-stream return link, long-title wrapping, no-upcoming state, default-image fallback, row layout, and narrow viewport behavior. Narrow viewport cropping is expected.
- [x] Phase 2: Add an optional thumbnail URL field to `model/QueueStream.py`; a legacy constructor call without the field defaults it to `None`.
- [x] Phase 2: Derive a YouTube thumbnail URL from the URI host and `remoteId` for existing records that omit the new field; other hosts remain unset.
- [x] Phase 2: Verify previously imported QueueStreams without a stored thumbnail remain loadable and can display a derived YouTube thumbnail; user confirmed this works.
- [x] Phase 2: Populate the field in the active YouTube fetch path in `services/FetchService.py` from yt-dlp's `thumbnail`, with a video-ID-based fallback URL.
- [x] Phase 2: Render the thumbnail URL in `templates/play.html`, falling back to `/static/default.png`; user confirmed thumbnails display as expected.
- [x] Phase 2: User tested YouTube fetch and confirmed thumbnails are persisted/displayed as expected.
- [x] Phase 3: Inspect the supplied Odysee channel feed and map its per-item `itunes:image` `href` into `QueueStream.thumbnailUrl`; retain the default fallback where no usable URL exists.
- [x] Phase 3: User tested Odysee fetch and confirmed newly fetched thumbnails display as expected; previously fetched Odysee items may continue using the default image.

## Validation

- User confirmed the fixed four-column grid behaves as expected across rows, the final-stream return link, long-title wrapping, no-upcoming state, default-image fallback, and narrow viewport behavior. Cropping on narrow viewports is expected.
- `python -m compileall -q model/QueueStream.py services/FetchService.py` passed.
- Runtime constructor checks passed: a legacy-shaped YouTube record derives an `hqdefault` URL, a non-YouTube record stays unset, and an explicit URL is retained.
- Mocked `FetchService.fetchYoutubeYdl` check passed for both a yt-dlp-provided thumbnail and the video-ID fallback.
- Source checks confirmed the active fetch path assigns `thumbnailUrl` and the template falls back to the local default image.
- User confirmed YouTube thumbnails render, including for previously imported QueueStreams without a stored thumbnail.
- User tested YouTube fetch and confirmed fetched thumbnails work in the application.
- Odysee RSS request returned HTTP 200 with XML. The first five video items each contained an `itunes:image` element with a distinct `href` on `thumbs.odycdn.com`.
- Mocked `FetchService.fetchOdysee` check passed for an item with `itunes:image` and one without it; the latter kept `thumbnailUrl` unset for the template fallback.
- No Odysee video or thumbnail files were downloaded during inspection or validation.
- User tested Odysee fetch and confirmed newly fetched thumbnails work in the application. Previously fetched Odysee items do not have thumbnails, which is accepted for this task.

## Notes / considerations

- Odysee RSS items in the supplied channel use the iTunes podcast namespace's `image` element with the URL in its `href` attribute. This is per-video metadata and can be used directly without downloading the image.
- Previously fetched Odysee QueueStreams are not retroactively updated with thumbnail URLs; this is intentional for the current scope.
- Rumble thumbnail support is deferred because the user noted its fetch implementation is incomplete.

## Results

- Phase 1: Replaced the shared Bootstrap row layout in `templates/play.html` with a dedicated grid, title/source text below each image, and the existing default-image fallback. Both `server.py` and `server_refactor.py` provide up to 16 upcoming streams; `static/css/style.css` places them in fixed four-column rows, including incomplete rows, with a 15rem minimum and horizontal scrolling on narrow screens. The user confirmed phase-one behavior, including the final item and narrow viewport.
- Phase 2: Added optional `QueueStream.thumbnailUrl`, populated it from YouTube yt-dlp entries with an `hqdefault` URL fallback, derived thumbnails for existing YouTube records with a remote ID, and updated the upcoming-video image to use the value or the local default image. A mocked fetch check verified both thumbnail sources; the user confirmed YouTube fetching and display.
- Phase 3: `FetchService.fetchOdysee` reads each RSS item's namespaced `itunes:image` `href` and passes it into `QueueStream.thumbnailUrl`. Missing image elements remain unset and use the existing template fallback. A mocked fetch check passed; the user confirmed Odysee fetching and display for new QueueStreams. Existing Odysee streams are not backfilled.
- App/browser validation was performed by the user; no app was run by the agent.
