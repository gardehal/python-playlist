# Add Audio-Only Playlist Downloads with MP3 Tags

## Problem

Before implementation, audio-only download was partially scaffolded but not connected end-to-end:

- `DownloadService.download()` and `downloadYoutube()` accept `audioOnly`, but the active yt-dlp options always select video plus audio.
- The CLI download command has no audio-only flag and `PlaylistCliController.downloadPlaylist()` does not pass one.
- The web playlist route reads an `audioOnly` query parameter using a string-to-bool comparison that is always false, and the playlist page has no audio-only control.
- `setMp3Metadata()` writes title and artist only; album, year, and track tags are comments and the helper is not called.
- `mutagen` is imported but absent from `requirements.txt`. MP3 conversion may also require FFmpeg, which is not currently documented as a prerequisite.

## Decisions

- D1: Audio-only is an explicit opt-in; regular video downloads must remain unchanged.
- D2: Audio-only output is MP3 with ID3 metadata.
- D3: Confirmed with user: track numbers are one-based in original playlist order. Preserve the original song title in ID3 metadata; minimally sanitize its filename form to remove filesystem-incompatible symbols.
- D4: Initial audio-only source scope is YouTube only (confirmed with user); other sources are intentionally unsupported for now.
- D5: Selected-range downloads and custom naming/output-directory options are not needed. Track numbers reflect each item's one-based position in the original playlist.
- D6: Use yt-dlp's `FFmpegExtractAudio` postprocessor for MP3 conversion; add no Python conversion dependency. Require FFmpeg to be discoverable before starting audio-only downloads.
- D7: Before web audio download, show a modal with editable album/folder name, artist, year, and genre. Default album/folder to the playlist name; prefill artist only when the playlist has one consistent source name; leave unavailable optional metadata blank.
- D8: Use Mutagen to write ID3 frames after yt-dlp/FFmpeg conversion. FFmpeg is an external executable; no Python audio-conversion dependency is added.
- D9: Save the playlist thumbnail and first video thumbnail as separate files in the album output folder. Choose the largest yt-dlp thumbnail variant with both dimensions at or below 1500px; only fetch HTTPS URLs from `ytimg.com` hosts, and do not fail audio downloads if artwork retrieval fails.

## Approach

1. Define and enforce the YouTube-only source gate for audio-only playlist downloads.
2. Add the audio-only modal to `templates/playlists/details.html` and pass its values through `server.py` to `DownloadPlaylistUseCase`.
3. Add a CLI audio-only option in `Commands.py` and pass it through `Main.py`; use playlist/source defaults when CLI metadata overrides are absent.
4. Pass audio-only and per-track metadata through `DownloadPlaylistUseCase` and `StreamDownloadProvider` to `YtDlpStreamDownloadProvider`.
5. Use the FFmpeg MP3 postprocessor and write ID3 title, artist, album, year, genre, and one-based track/total tags with Mutagen. Preserve original title in tags and minimally sanitize only its filename form.
6. Test web/CLI propagation, conversion options, filename sanitization, ID3 fields, missing metadata, and unchanged video downloads using mocked yt-dlp and local MP3 fixtures.

## Todos

- [x] Confirm audio-only source scope: YouTube only initially; other sources are deferred.
- [x] Confirm user-facing metadata fields, one-based track numbering, and minimally sanitized filename behavior.
- [x] Add CLI audio-only flag and pass it through `Commands.py` and `Main.py` to `DownloadPlaylistUseCase`.
- [x] Add web audio-only modal and pass album/artist/year/genre to the active download route.
- [x] Implement yt-dlp audio extraction and MP3 conversion while preserving the regular video path.
- [x] Preflight FFmpeg availability and warn/abort before starting an audio-only download when it is missing.
- [x] Reject audio-only requests containing non-YouTube web streams before downloading any playlist item; surface the reason before web background work starts.
- [x] Pass album, artist, year, genre, song title, and original one-based track number/total through the download use case to the provider.
- [x] Write title, artist-if-present, album, year-if-present, genre-if-present, and track ID3 tags with Mutagen.
- [x] Pin Mutagen in `requirements.txt`.
- [x] Add tests for option propagation, format selection, ID3 tags, missing metadata, and unchanged video downloads.
- [x] Save playlist and first-video thumbnails as `cover-playlist` and `cover-video` files alongside audio downloads.
- [x] Confirm audio-only downloads work with the user.
- [x] Confirm custom naming and output-directory options are not needed; the active CLI continues to reject them.

## Notes / considerations

- `QueueStream.publishedAt` is optional and may not be populated by every fetch path. The modal should leave year blank when unavailable unless a fallback is confirmed.
- FFmpeg is an external executable, not a Python requirement; the current web route checks for it before scheduling audio-only work.
- The web modal passes editable album, artist, year, and genre; CLI audio-only mode uses playlist/source defaults and has no metadata prompt.
- The old `DownloadService` helper is not used by the active CompositionRoot path. `YtDlpStreamDownloadProvider` handles conversion and Mutagen ID3 writing.
- Audio-only playlist requests are gated to YouTube web QueueStreams; a mixed/non-YouTube playlist is rejected before any item download. Video downloads remain unaffected.
- Selected-range downloads, custom naming/output-directory options, and README usage documentation are not needed, per user decision on 2026-11-15.

## Validation

- Existing video-only downloads remain unchanged with the option disabled.
- CLI and web audio-only options reach `DownloadPlaylistUseCase` as `True` only when selected.
- The user reports that audio-only downloads work. The interface used and real-file ID3 inspection were not specified.
- Missing year/artist metadata does not fail the download or create fabricated values.
- Mocked tests cover one-based track numbers and ID3 metadata; selected ranges are out of scope.

## Results

- Added yt-dlp's `FFmpegExtractAudio` postprocessor for audio-only MP3 conversion without adding a Python package; video format selection remains unchanged.
- Added an FFmpeg preflight to the provider, download use case, and web route so the route warns and aborts before starting its background thread when FFmpeg is unavailable.
- Verified the preflight with FFmpeg mocked absent, MP3 postprocessor options, and unchanged video options.
- `python -m unittest discover -s tests -p "test*.py" -q` passed 83 tests after the thumbnail-host guard; `compileall` passed for all changed Python modules and tests.
- FFmpeg is available in this environment at `C:\ffmpeg\ffmpeg.exe`.
- User confirmed one-based original playlist track numbering, minimally sanitized filename titles with original ID3 titles preserved, and a web modal for editable album/folder name, artist, year, and genre.
- Web and CLI pass audio-only mode to the use case; the web modal passes editable metadata and Mutagen writes the expected ID3 frames in a local-file test.
- Audio-only use-case and web-route tests reject a mixed YouTube/Odysee playlist before any background download starts.
- Playlist and first-video thumbnail URLs flow into audio download metadata; the downloader saves each image once in the album folder, with URL selection capped at the largest available variant no wider or taller than 1500px.
- Thumbnail downloads are restricted to HTTPS `ytimg.com` hosts; unsupported URLs and image-fetch failures do not block MP3 downloads.
- On 2026-11-15 the user confirmed audio-only downloads work; the tested interface and real-file tag inspection were not specified. Missing-FFmpeg behavior is covered with a mocked preflight.
