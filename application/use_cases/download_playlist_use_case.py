from typing import NamedTuple

from exceptions.domain_exceptions import PlaylistNotFoundError
from ports.playlist_repository import PlaylistRepository
from ports.queue_stream_repository import QueueStreamRepository
from ports.stream_download_provider import StreamDownloadProvider


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

    def execute(self, playlist_id: str, audio_only: bool = False) -> DownloadPlaylistResult:
        playlist = self._playlist_repository.get_by_id(playlist_id)
        if playlist is None:
            raise PlaylistNotFoundError(f"Playlist with ID {playlist_id} not found.")

        downloaded_count = 0
        skipped_count = 0
        failed_count = 0
        for stream_id in playlist.streamIds:
            stream = self._queue_stream_repository.get_by_id(stream_id)
            if stream is None or not stream.isWeb:
                skipped_count += 1
                continue

            try:
                result = self._stream_download_provider.download_stream(
                    stream.uri,
                    playlist.name,
                    audio_only,
                )
            except Exception:
                failed_count += 1
                continue

            if result:
                downloaded_count += 1
            else:
                failed_count += 1

        return DownloadPlaylistResult(downloaded_count, skipped_count, failed_count)
