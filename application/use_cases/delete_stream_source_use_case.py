from ports.stream_source_repository import StreamSourceRepository
from exceptions.domain_exceptions import StreamSourceError

class DeleteStreamSourceUseCase:
    """
    Use Case to delete a stream source from the system.
    """

    def __init__(self, stream_source_repository: StreamSourceRepository) -> None:
        self._stream_source_repository = stream_source_repository

    def execute(self, stream_source_id: str) -> None:
        """
        Executes the logic to delete a stream source.

        Raises:
            StreamSourceError: If the source is not found or deletion fails.
        """
        source = self._stream_source_repository.get_by_id(stream_source_id)
        if not source:
            raise StreamSourceError(f"StreamSource with ID {stream_source_id} not found.")
            
        self._stream_source_repository.delete(stream_source_id)
