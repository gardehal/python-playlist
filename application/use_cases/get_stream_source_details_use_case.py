from typing import Optional
from ports.stream_source_repository import StreamSourceRepository
from model.StreamSource import StreamSource

class GetStreamSourceDetailsUseCase:
    """
    Use Case to get details of a specific stream source.
    """

    def __init__(self, stream_source_repository: StreamSourceRepository) -> None:
        self._stream_source_repository = stream_source_repository

    def execute(self, stream_source_id: str) -> Optional[StreamSource]:
        """
        Executes the logic to retrieve a stream source by ID.

        Returns:
            Optional[StreamSource]: The found stream source or None if not found.
        """
        return self._stream_source_repository.get_by_id(stream_source_id)
