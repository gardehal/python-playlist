from ports.playlist_repository import PlaylistRepository
from ports.queue_stream_repository import QueueStreamRepository
from ports.stream_source_repository import StreamSourceRepository


class PurgeSoftDeletedEntitiesUseCase:
    def __init__(
        self,
        playlist_repository: PlaylistRepository,
        queue_stream_repository: QueueStreamRepository,
        stream_source_repository: StreamSourceRepository,
    ) -> None:
        self._playlist_repository = playlist_repository
        self._queue_stream_repository = queue_stream_repository
        self._stream_source_repository = stream_source_repository

    def execute(self) -> bool:
        repositories = (
            self._queue_stream_repository,
            self._stream_source_repository,
            self._playlist_repository,
        )
        for repository in repositories:
            for entity in repository.get_all(include_deleted=True):
                if entity.deleted:
                    repository.remove(entity.id, include_deleted=True)
        return True
