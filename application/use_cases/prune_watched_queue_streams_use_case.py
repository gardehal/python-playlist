from typing import List

from model.QueueStream import QueueStream
from ports.playlist_repository import PlaylistRepository
from ports.queue_stream_repository import QueueStreamRepository


class PruneWatchedQueueStreamsUseCase:
    def __init__(
        self,
        playlist_repository: PlaylistRepository,
        queue_stream_repository: QueueStreamRepository,
    ) -> None:
        self._playlist_repository = playlist_repository
        self._queue_stream_repository = queue_stream_repository

    def execute(self, playlist_id: str) -> List[QueueStream]:
        playlist = self._playlist_repository.get_by_id(playlist_id)
        if playlist is None or playlist.playWatchedStreams:
            return []

        watched_streams = [
            stream
            for stream_id in playlist.streamIds
            if (stream := self._queue_stream_repository.get_by_id(stream_id)) is not None
            and stream.watched
        ]
        if not watched_streams:
            return []

        watched_stream_ids = {stream.id for stream in watched_streams}
        for stream in watched_streams:
            self._queue_stream_repository.delete(stream.id)

        playlist.streamIds = [
            stream_id for stream_id in playlist.streamIds if stream_id not in watched_stream_ids
        ]
        self._playlist_repository.save(playlist)
        return watched_streams
