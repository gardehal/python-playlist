from datetime import datetime
import ntpath
from typing import Optional
from urllib.parse import urlparse
from ports.external_stream_provider import ExternalStreamProvider
from ports.queue_stream_repository import QueueStreamRepository
from model.QueueStream import QueueStream

class CreateQueueStreamUseCase:
    """
    Use Case to create a new QueueStream.
    """

    def __init__(self, queue_stream_repository: QueueStreamRepository,
                 external_stream_provider: Optional[ExternalStreamProvider] = None) -> None:
        self._queue_stream_repository = queue_stream_repository
        self._external_stream_provider = external_stream_provider

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
        normalized_name = name.strip() if name else ""
        if not normalized_name and uri:
            is_web_uri = urlparse(uri).scheme.lower() in {"http", "https"}
            if is_web or is_web_uri:
                if self._external_stream_provider is None:
                    raise ValueError("Could not determine a name for the web URI.")
                try:
                    metadata = self._external_stream_provider.fetch_metadata(uri)
                    normalized_name = (metadata.get("name") or "").strip()
                except Exception as error:
                    raise ValueError("Could not determine a name for the web URI.") from error
            else:
                normalized_name = ntpath.basename(uri.rstrip("/\\"))

        if not normalized_name:
            raise ValueError("Enter a name or provide a URI with a detectable title.")

        queue_stream = QueueStream(
            name=normalized_name,
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
