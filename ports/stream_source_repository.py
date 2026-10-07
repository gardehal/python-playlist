from abc import ABC, abstractmethod
from typing import List, Optional
from model.StreamSource import StreamSource

class StreamSourceRepository(ABC):
    """Interface for stream source data access."""

    @abstractmethod
    def get_by_id(self, stream_source_id: str) -> Optional[StreamSource]:
        """Retrieve a stream source by its unique identifier."""
        pass

    @abstractmethod
    def save(self, stream_source: StreamSource) -> None:
        """Persist a stream source to the storage backend."""
        pass

    @abstractmethod
    def delete(self, stream_source_id: str) -> None:
        """Remove a stream source from the storage backend."""
        pass

    @abstractmethod
    def get_all(self) -> List[StreamSource]:
        """Retrieve all available stream sources."""
        pass
