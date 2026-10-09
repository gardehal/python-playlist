from ports.queue_stream_repository import QueueStreamRepository

class DeleteQueueStreamUseCase:
    """
    Use Case to delete a QueueStream.
    """

    def __init__(self, queue_stream_repository: QueueStreamRepository) -> None:
        self._queue_stream_repository = queue_stream_repository

    def execute(self, queue_stream_id: str) -> None:
        """
        Executes the logic to delete a queue stream.
        """
        self._queue_stream_repository.delete(queue_stream_id)
