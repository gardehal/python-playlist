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

- [ ] Verify `pytubefix` call sites and replace YouTube title extraction in `services/SharedService.py` with yt-dlp.
- [ ] Remove the unused legacy YouTube channel fetch path and `Channel` import from `services/FetchService.py`.
- [ ] Remove the unreachable pytubefix download branch from `services/DownloadService.py` while preserving active yt-dlp behavior.
- [ ] Test title lookup and active fetch behavior without pytubefix installed.
- [ ] Validate yt-dlp download behavior, especially the previously problematic sample set if available; retain the dependency until this gate passes.
- [ ] Remove `pytubefix` from `requirements.txt` and search the repository for remaining imports/usages.
- [ ] Update the README TODO and the current-state summary in `docs/plans/2026-08-16-youtube-download-evolution.md`.
- [ ] Confirm failure messages and output naming remain usable; document the Node.js prerequisite for YouTube downloads.

## Notes / considerations

- The current `DownloadService` yt-dlp branch configures Node.js when found. A missing Node.js runtime may affect the historical failure cases; verify this before claiming equivalent download coverage.
- `audioOnly` is ignored in the active yt-dlp branch today; supporting it is separate work and is not included here.
- The repository currently has a debug download script rather than a structured YouTube migration test suite. Avoid tests that download long videos; use mocked yt-dlp calls for unit coverage and short representative manual checks for integration.
- The existing download-evolution note describes earlier attempts and a fallback that does not match the current hardcoded branch selection. Preserve its historical experiments but correct its current-state summary after validation.

## Validation

- Run Python syntax checks and the repository's available tests after removing pytubefix imports.
- Mock yt-dlp metadata extraction and verify `SharedService.getPageTitle` returns sanitized titles and handles failures.
- Verify active YouTube fetch and playlist-import paths still work without pytubefix installed.
- Exercise representative short-video downloads with and without Node.js where available; do not download long videos.
- Search for `pytubefix` across source and dependency files; only historical documentation may remain.

## Results
