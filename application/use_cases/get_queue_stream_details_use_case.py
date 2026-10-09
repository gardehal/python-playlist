from typing import Optional
from ports.queue_stream_repository import QueueStreamRepository
from model.QueueStream import QueueStream

class GetQueueStreamDetailsUseCase:
    """
    Use Case to get details of a specific queue stream.
    """

    def __init__(self, queue_stream_repository: QueueStreamRepository) -> None:
        self._queue_stream_repository = queue_stream_repository

    def execute(self, queue_stream_id: str) -> Optional[QueueStream]:
        """
        Executes the logic to retrieve a queue stream by ID.

        Returns:
            Optional[Queue[QueueStream]]: The found queue stream or None if not found.
        """
        return self._queue_stream_repository.get_by_id(queue_stream_id)
