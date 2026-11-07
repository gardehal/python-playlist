from datetime import datetime
from typing import Optional
from ports.queue_stream_repository import QueueStreamRepository
from model.QueueStream import QueueStream

class CreateQueueStreamUseCase:
    """
    Use Case to create a new QueueStream.
    """

    def __init__(self, queue_stream_repository: QueueStreamRepository) -> None:
        self._queue_stream_repository = queue_stream_repository

    def execute(self, name: str, uri: str, is_web: bool, 
                stream_source_id: Optional[str] = None,
                stream_source_name: Optional[str] = None,
                watched: Optional[datetime] = None,
                background_content: bool = False,
                playtime_seconds: Optional[int] = None,
                remote_id: Optional[str] = None) -> QueueStream:
        """
        Executes the logic to create a new queue stream.

        Returns:
            QueueStream: The newly created queue stream object.
        """
        queue_stream = QueueStream(
            name=name,
            uri=uri,
            isWeb=is_web,
            streamSourceId=stream_source_id,
            streamSourceName=stream_source_name,
            watched=watched,
            backgroundContent=background_content,
            playtimeSeconds=playtime_seconds,
            remoteId=remote_id
        )
        self._queue_stream_repository.save(queue_stream)
        return queue_stream
