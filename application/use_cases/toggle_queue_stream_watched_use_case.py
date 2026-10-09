from typing import Optional
from ports.queue_stream_repository import QueueStreamRepository
from model.QueueStream import QueueStream
from grdUtil.DateTimeUtil import getDateTime

class ToggleQueueStreamWatchedUseCase:
    """
    Use Case to toggle the 'watched' state of a QueueStream.
    """

    def __init__(self, queue_stream_repository: QueueStreamRepository) -> None:
        self._queue_stream_repository = queue_stream_repository

    def execute(self, queue_stream_id: str) -> QueueStream:
        """
        Executes the logic to toggle the watched timestamp.

        Returns:
            QueueStream: The updated queue stream object.

        Raises:
            ValueError: If the queue stream is not found.
        """
        queue_stream = self._queue_stream_repository.get_by_id(queue_stream_id)
        if not queue_stream:
            raise ValueError(f"QueueStream with ID {queue_stream_id} not found.")

        # Toggle watched state
        if queue_stream.watched:
            queue_stream.watched = None
        else:
            queue_stream.watched = getDateTime()

        self._queue_stream_repository.save(queue_stream)
        return queue_stream
