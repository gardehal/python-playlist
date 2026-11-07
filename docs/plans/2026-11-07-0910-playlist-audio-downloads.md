# Add Audio-Only Playlist Downloads with MP3 Tags

## Problem

Audio-only download is partially scaffolded but not connected end-to-end:

- `DownloadService.download()` and `downloadYoutube()` accept `audioOnly`, but the active yt-dlp options always select video plus audio.
- The CLI download command has no audio-only flag and `PlaylistCliController.downloadPlaylist()` does not pass one.
- The web playlist route reads an `audioOnly` query parameter using a string-to-bool comparison that is always false, and the playlist page has no audio-only control.
- `setMp3Metadata()` writes title and artist only; album, year, and track tags are comments and the helper is not called.
- `mutagen` is imported but absent from `requirements.txt`. MP3 conversion may also require FFmpeg, which is not currently documented as a prerequisite.

## Decisions

- D1: Audio-only is an explicit opt-in; regular video downloads must remain unchanged.
- D2: Audio-only output is MP3 with ID3 metadata.
- D3: Proposed tag mapping, needs confirmation: title from `QueueStream.name`, album from `Playlist.name`, track number from one-based playlist position, artist from `QueueStream.streamSourceName`, and year from source publication metadata when available (otherwise omit).
- D4: Initial source scope is TBD: YouTube only is the smallest coherent slice; Odysee audio-only would require a separate source path/strategy.
- D5: Preserve playlist selection ranges and custom naming behavior; track number should reflect the item's position in the original playlist, not its position in a selected subrange.

## Approach

1. Confirm D3 and D4 before implementation. Define missing-metadata behavior and whether an audio-only option applies to CLI, web, or both.
2. Add an audio-only flag to the CLI download command in `Commands.py`, pass it through `Main.py` and `PlaylistCliController.downloadPlaylist()`, and add a corresponding control to `templates/playlists/details.html` and the playlist download routes in `server.py` and `server_refactor.py`. Parse the web value as a real boolean.
3. In `services/DownloadService.py`, select best audio for audio-only mode and use yt-dlp's FFmpeg postprocessor to produce MP3. Keep the current video format and behavior for regular downloads.
4. Pass playlist metadata to the per-stream download operation: album, track number/total, and available title, artist, and year. Write ID3 title, artist, album, year, and track frames with Mutagen after conversion.
5. Add `mutagen` to `requirements.txt` if retained as the tag writer, and document FFmpeg (and the existing Node.js caveat) as required runtime tooling for YouTube downloads.
6. Add focused tests for CLI/web option propagation, yt-dlp format selection, tag creation, missing metadata, and unchanged video downloads. Use mocked yt-dlp and local MP3 fixtures; use a short real download only for manual integration validation.

## Todos

- [ ] Confirm source scope: YouTube only initially, or YouTube and Odysee.
- [ ] Confirm MP3 tag mapping for artist and year; proposed mapping is in D3.
- [ ] Add CLI audio-only flag and pass it through `Main.py` and `PlaylistCliController.py`.
- [ ] Add web audio-only control and correct boolean parsing in both playlist download routes.
- [ ] Implement yt-dlp audio extraction and MP3 conversion while preserving the regular video path.
- [ ] Pass playlist name and original one-based track position into audio download metadata.
- [ ] Write title, artist, album, year-if-known, and track ID3 tags with Mutagen.
- [ ] Add or verify `mutagen` dependency and document FFmpeg/Node.js prerequisites.
- [ ] Add tests for option propagation, format selection, ID3 tags, range selection, and video-path regression.
- [ ] Verify audio-only downloads through CLI and web using a short sample; verify tags with Mutagen or a media inspector.
- [ ] Update README audio-download TODO and usage documentation.

## Notes / considerations

- `QueueStream.publishedAt` is optional and may not be populated by every fetch path. Year should be omitted when unavailable unless a different fallback is confirmed.
- The current web route's `request.args.get(...).lower() is True` test never enables audio-only mode.
- FFmpeg is an external executable, not a Python requirement; MP3 output from yt-dlp may fail without it.
- `DownloadService` currently accepts `audioOnly` but ignores it. The existing `setMp3Metadata()` helper is not called and does not yet write album/year/track tags.

## Validation

- Existing video-only downloads remain unchanged with the option disabled.
- CLI and web audio-only options both reach `DownloadService` as `True` only when selected.
- Audio output is MP3, opens as valid audio, and includes the agreed ID3 fields.
- Missing year/artist metadata does not fail the download or create fabricated values.
- Track numbers remain based on original playlist order when a range is selected.
- Short real YouTube sample downloads succeed when FFmpeg and the configured yt-dlp runtime are available.

## Results
