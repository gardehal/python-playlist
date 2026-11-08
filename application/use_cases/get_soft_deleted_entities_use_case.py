from model.PlaylistDetailed import PlaylistDetailed
from ports.playlist_repository import PlaylistRepository
from ports.queue_stream_repository import QueueStreamRepository
from ports.stream_source_repository import StreamSourceRepository


class GetSoftDeletedEntitiesUseCase:
    def __init__(
        self,
        playlist_repository: PlaylistRepository,
        queue_stream_repository: QueueStreamRepository,
        stream_source_repository: StreamSourceRepository,
    ) -> None:
        self._playlist_repository = playlist_repository
        self._queue_stream_repository = queue_stream_repository
        self._stream_source_repository = stream_source_repository

    def execute(self) -> PlaylistDetailed:
        return PlaylistDetailed(
            playlists=[entity for entity in self._playlist_repository.get_all(include_deleted=True) if entity.deleted],
            queueStreams=[entity for entity in self._queue_stream_repository.get_all(include_deleted=True) if entity.deleted],
            streamSources=[entity for entity in self._stream_source_repository.get_all(include_deleted=True) if entity.deleted],
        )
