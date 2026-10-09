from typing import Optional
from ports.queue_stream_repository import QueueStreamRepository
from model.QueueStream import QueueStream

class UpdateQueueStreamUseCase:
    """
    Use Case to update an existing QueueStream.
    """

    def __init__(self, queue_stream_repository: QueueStreamRepository) -> None:
        self._queue_stream_repository = queue_stream_repository

    def execute(self, queue_stream_id: str, name: Optional[str] = None, 
                uri: Optional[str] = None, is_web: Optional[bool] = None, 
                stream_source_id: Optional[str] = None, 
                stream_source_name: Optional[str] = None, 
                watched: Optional[any] = None) -> QueueStream:
        """
        Executes the logic to update a queue stream.

        Returns:
            QueueStream: The updated queue stream object.
        """
        queue_stream = self._queue_stream_repository.get_by_id(queue_stream_id)
        if not queue_stream:
            raise ValueError(f"QueueStream with ID {queue_stream_id} not found.")

        if name is not None:
            queue_stream.name = name
        if uri is not None:
            queue_stream.uri = uri
        if is_web is not None:
            queue_stream.isWeb = is_web
        if stream_source_id is not None:
            queue_stream.streamSourceId = stream_source_id
        if stream_source_name is not None:
            queue_stream.streamSourceName = stream_source_name
        if watched is not None:
            queue_stream.watched = watched

        self._queue_stream_repository.save(queue_stream)
        return queue_stream
