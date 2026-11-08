from copy import copy
from typing import List

from model.Playlist import Playlist
from ports.playlist_repository import PlaylistRepository
from ports.queue_stream_repository import QueueStreamRepository


class CopyQueueStreamToPlaylistsUseCase:
    def __init__(
        self,
        playlist_repository: PlaylistRepository,
        queue_stream_repository: QueueStreamRepository,
    ) -> None:
        self._playlist_repository = playlist_repository
        self._queue_stream_repository = queue_stream_repository

    def execute(self, queue_stream_id: str, playlist_ids: List[str]) -> List[Playlist]:
        source_stream = self._queue_stream_repository.get_by_id(queue_stream_id)
        if source_stream is None:
            raise ValueError(f"QueueStream with ID {queue_stream_id} not found.")

        added_playlists = []
        for playlist_id in dict.fromkeys(playlist_ids):
            playlist = self._playlist_repository.get_by_id(playlist_id)
            if playlist is None:
                continue

            if not playlist.allowDuplicates:
                existing_streams = (
                    self._queue_stream_repository.get_by_id(stream_id)
                    for stream_id in playlist.streamIds
                )
                if any(
                    stream is not None
                    and (stream.uri == source_stream.uri or stream.name == source_stream.name)
                    for stream in existing_streams
                ):
                    continue

            copied_stream = copy(source_stream)
            copied_stream.id = None
            self._queue_stream_repository.save(copied_stream)
            if copied_stream.id is None:
                raise RuntimeError("QueueStream repository did not assign an ID to the copy.")

            playlist.streamIds.append(copied_stream.id)
            try:
                self._playlist_repository.save(playlist)
            except Exception:
                playlist.streamIds.remove(copied_stream.id)
                self._queue_stream_repository.delete(copied_stream.id)
                raise

            added_playlists.append(playlist)

        return added_playlists
