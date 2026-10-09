from typing import List, Optional
from ports.queue_stream_repository import QueueStreamRepository
from model.QueueStream import QueueStream

class GetAllQueueStreamsUseCase:
    """
    Use Case to get all queue streams.
    """

    def __init__(self, queue_stream_repository: QueueStreamRepository) -> None:
        self._queue_stream_repository = queue_stream_repository

    def execute(self) -> List[QueueStream]:
        """
        Executes the logic to retrieve all queue streams.

        Returns:
            List[QueueStream]: A list of all queue streams.
        """
        return self._queue_stream_repository.get_all()
