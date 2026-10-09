from typing import Optional
from ports.stream_source_repository import StreamSourceRepository
from model.StreamSource import StreamSource
from exceptions.domain_exceptions import StreamSourceError

class UpdateStreamSourceUseCase:
    """
    Use Case to update an existing stream source.
    """

    def __init__(self, stream_source_repository: StreamSourceRepository) -> None:
        self._stream_source_repository = stream_source_repository

    def execute(self, stream_source_id: str, name: Optional[str] = None, 
                uri: Optional[str] = None, is_web: Optional[bool] = None, 
                stream_source_type_id: Optional[int] = None, 
                enable_fetch: Optional[bool] = None) -> StreamSource:
        """
        Executes the logic to update a stream source.

        Returns:
            StreamSource: The updated stream source object.

        Raises:
            StreamSourceError: If the source is not found or update fails.
        """
        source = self._stream_source_repository.get_by_id(stream_source_id)
        if not source:
            raise StreamSourceError(f"StreamSource with ID {stream_source_id} not found.")

        if name is not None:
            source.name = name
        if uri is not None:
            source.uri = uri
        if is_web is not None:
            source.isWeb = is_web
        if stream_source_type_id is not None:
            source.streamSourceTypeId = stream_source_type_id
        if enable_fetch is not None:
            source.enableFetch = enable_fetch

        self._stream_source_repository.save(source)
        return source
    
