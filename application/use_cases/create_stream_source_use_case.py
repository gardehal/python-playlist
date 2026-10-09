from typing import Optional
from ports.stream_source_repository import StreamSourceRepository
from model.StreamSource import StreamSource
from exceptions.domain_exceptions import StreamSourceError

class CreateStreamSourceUseCase:
    """
    Use Case to create a new stream source.
    """

    def __init__(self, stream_source_repository: StreamSourceRepository) -> None:
        self._stream_source_repository = stream_source_repository

    def execute(self, name: str, uri: str, is_web: bool, 
                stream_source_type_id: int = 0, enable_fetch: bool = True) -> StreamSource:
        """
        Executes the logic to create a new stream source.

        Returns:
            StreamSource: The newly created stream source object.

        Raises:
            StreamSourceError: If validation fails or creation fails.
        """
        # In a real scenario, we might add validation here (e.g., URI format)
        new_source = StreamSource(
            name=name,
            uri=uri,
            isWeb=is_web,
            streamSourceTypeId=stream_source_type_id,
            enableFetch=enable_fetch
        )
        
        self._stream_source_repository.save(new_source)
        return new_source
