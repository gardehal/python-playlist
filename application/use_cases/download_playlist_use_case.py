from typing import NamedTuple
from urllib.parse import urlparse

from exceptions.domain_exceptions import PlaylistNotFoundError
from ports.playlist_repository import PlaylistRepository
from ports.queue_stream_repository import QueueStreamRepository
from ports.stream_download_provider import AudioDownloadMetadata, StreamDownloadProvider


class DownloadPlaylistResult(NamedTuple):
    downloaded_count: int
    skipped_count: int
    failed_count: int


class DownloadPlaylistUseCase:
    def __init__(
        self,
        playlist_repository: PlaylistRepository,
        queue_stream_repository: QueueStreamRepository,
        stream_download_provider: StreamDownloadProvider,
    ) -> None:
        self._playlist_repository = playlist_repository
        self._queue_stream_repository = queue_stream_repository
        self._stream_download_provider = stream_download_provider

    def validate_options(self, audio_only: bool = False) -> None:
        self._stream_download_provider.validate_options(audio_only)

    def validate_playlist_options(self, playlist_id: str, audio_only: bool = False) -> None:
        self.validate_options(audio_only)
        if not audio_only:
            return

        playlist = self._playlist_repository.get_by_id(playlist_id)
        if playlist is None:
            raise PlaylistNotFoundError(f"Playlist with ID {playlist_id} not found.")

        for stream_id in playlist.streamIds:
            stream = self._queue_stream_repository.get_by_id(stream_id)
            if stream is None or not stream.isWeb:
                continue

            host = (urlparse(stream.uri).hostname or "").lower()
            is_youtube_host = (
                host == "youtu.be"
                or host == "youtube.com"
                or host.endswith(".youtube.com")
                or host == "youtube-nocookie.com"
                or host.endswith(".youtube-nocookie.com")
            )
            if not is_youtube_host:
                raise ValueError(
                    "Audio-only MP3 downloads currently support YouTube QueueStreams only. "
                    f"Unsupported stream: {stream.name or stream.uri}"
                )

    def execute(
        self,
        playlist_id: str,
        audio_only: bool = False,
        album: str = None,
        artist: str = None,
        year: str = None,
        genre: str = None,
    ) -> DownloadPlaylistResult:
        playlist = self._playlist_repository.get_by_id(playlist_id)
        if playlist is None:
            raise PlaylistNotFoundError(f"Playlist with ID {playlist_id} not found.")

        self.validate_playlist_options(playlist_id, audio_only)

        downloaded_count = 0
        skipped_count = 0
        failed_count = 0
        track_total = len(playlist.streamIds)
        first_video_thumbnail_url = None
        if audio_only:
            for stream_id in playlist.streamIds:
                candidate = self._queue_stream_repository.get_by_id(stream_id)
                if candidate is not None and candidate.isWeb:
                    first_video_thumbnail_url = candidate.thumbnailUrl
                    break

        for track_number, stream_id in enumerate(playlist.streamIds, start=1):
            stream = self._queue_stream_repository.get_by_id(stream_id)
            if stream is None or not stream.isWeb:
                skipped_count += 1
                continue

            audio_metadata = None
            if audio_only:
                audio_metadata = AudioDownloadMetadata(
                    title=stream.name or "",
                    album=(album or "").strip() or playlist.name,
                    artist=(artist or "").strip() or stream.streamSourceName,
                    year=(year or "").strip() or None,
                    genre=(genre or "").strip() or None,
                    track_number=track_number,
                    track_total=track_total,
                    playlist_thumbnail_url=getattr(playlist, "thumbnailUrl", None),
                    video_thumbnail_url=first_video_thumbnail_url,
                )

            try:
                result = self._stream_download_provider.download_stream(
                    stream.uri,
                    playlist.name,
                    audio_only,
                    metadata=audio_metadata,
                )
            except Exception:
                failed_count += 1
                continue

            if result:
                downloaded_count += 1
            else:
                failed_count += 1

        return DownloadPlaylistResult(downloaded_count, skipped_count, failed_count)
