# Migrate Remaining pytubefix Usage to yt-dlp

Continues [YouTube download evolution](2026-08-16-youtube-download-evolution.md).

## Problem

`yt_dlp` already handles active YouTube channel fetching, YouTube playlist import, and the active branch of YouTube downloads. `pytubefix` remains imported by `SharedService`, the legacy `FetchService.fetchYoutube` method, and `DownloadService`'s dormant branch. `requirements.txt` still installs it.

The README suggests pytubefix is still a download fallback, but `DownloadService.downloadYoutube` currently hardcodes `useYtDlp = 1`, so that branch is unreachable. The previous download note records historical experiments and should be reconciled with current behavior when this migration lands.

## Decisions

- D1: Treat this as a follow-up to `2026-08-16-youtube-download-evolution.md`; preserve that document's experiment history and update only its current-state summary when appropriate.
- D2: Make yt-dlp the only YouTube implementation. Do not retain or add a pytubefix rescue fallback.
- D3: Replace pytubefix title lookup only for YouTube videos in `SharedService.getPageTitle`; preserve the existing non-YouTube lookup behavior.
- D4: Remove `FetchService.fetchYoutube` if call-site verification still shows it is unused; keep the active `fetchYoutubeYdl` path.
- D5: Keep audio-only support out of scope unless implementation requirements change. The active yt-dlp branch currently ignores `audioOnly`; do not imply that this migration fixes it.

## Approach

1. Replace the YouTube single-video title lookup in `services/SharedService.py` with yt-dlp metadata extraction using `download=False`; preserve the existing title sanitization and failure behavior.
2. Remove the unused pytubefix `Channel` import and legacy `FetchService.fetchYoutube` method after confirming there are no callers beyond commented-out dispatch code.
3. Simplify `services/DownloadService.py` to its currently active yt-dlp path and remove pytubefix imports and the unreachable branch. Preserve the existing Node.js runtime configuration, client selection, output naming, and error handling unless tests expose a required compatibility change.
4. Verify YouTube downloads against representative URLs, including previously problematic cases if that test set is available. If yt-dlp-only download behavior is not acceptable, stop before removing the dependency and revise the migration decision rather than restoring an unverified fallback.
5. Remove `pytubefix` from `requirements.txt` after all imports are gone. Update the README TODO and the current-state section of the prior download note to reflect the verified implementation and remaining runtime requirements.

## Todos

- [x] Verify `pytubefix` call sites and replace YouTube title extraction in `services/SharedService.py` with yt-dlp.
- [x] Remove the unused legacy YouTube channel fetch path and `Channel` import from `services/FetchService.py`.
- [x] Remove the unreachable pytubefix download branch from `services/DownloadService.py` while preserving active yt-dlp behavior.
- [x] Test mocked title lookup and import all three services with pytubefix imports blocked.
- [x] User verified CLI YouTube title lookup and a short-video download through the application.
- [x] Remove `pytubefix` from `requirements.txt`; no Python imports remain.
- [x] Remove the obsolete README TODO and update the current-state summary in `docs/plans/2026-08-16-youtube-download-evolution.md`.
- [x] User retested the previously failing YouTube titles; downloads succeeded.
- [x] Verify generated and custom filenames remove `!()'` while preserving the extension and generated-name separators.
- [x] Document the Node.js availability caveat for YouTube downloads in `README.md`; successful output naming was verified.
- [ ] Exercise the yt-dlp failure path and confirm the app reports the failure clearly.

## Notes / considerations

- The current `DownloadService` yt-dlp branch configures Node.js when found. Behavior for the historical failure cases without Node.js remains unverified.
- `audioOnly` is ignored in the active yt-dlp branch today; supporting it is separate work and is not included here.
- The repository currently has a debug download script rather than a structured YouTube migration test suite. Avoid tests that download long videos; use mocked yt-dlp calls for unit coverage and short representative manual checks for integration.
- The existing download-evolution note describes earlier attempts and a fallback that does not match the current hardcoded branch selection. Preserve its historical experiments but correct its current-state summary after validation.

## Validation

- `python -m compileall -q services/SharedService.py services/FetchService.py services/DownloadService.py` passed.
- Mocked `SharedService.getPageTitle` check passed for sanitized title and `download=False` metadata extraction.
- Mocked `DownloadService.downloadYoutube` check passed for metadata lookup, Node.js configuration, output path, and yt-dlp download invocation; no video was downloaded.
- `SharedService`, `FetchService`, and `DownloadService` imported with pytubefix imports blocked.
- Source search found no Python pytubefix imports; the legacy `fetchYoutube` name remains only in a commented-out dispatch line.
- `getVideoPath()` checks passed for default and custom names: `!()'` are removed, the extension is preserved, and generated underscores remain readable. No file was created.
- User confirmed CLI title lookup and a short-video download both work through the application.
- User retested the previously failing YouTube titles and confirmed downloads succeeded.
- Source/dependency search found no Python imports or requirement for `pytubefix`; historical documentation retains experiment context.
- A forced yt-dlp failure has not been tested through the app.

## Results

- Replaced the active YouTube title lookup with yt-dlp metadata extraction.
- Removed the unused pytubefix channel fetch implementation and the unreachable download branch.
- Sanitizes the filename stem with `grdUtil` mode 1 while preserving the extension and generated-name separators.
- Removed `pytubefix` from `requirements.txt`; updated README and historical download status.
- User verified CLI title lookup and downloaded titles that had previously failed. A forced failure case remains untested.
- `README.md` documents that Node.js should be available on `PATH` for YouTube JavaScript challenges.
