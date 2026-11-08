from typing import List, Optional
from model.QueueStream import QueueStream
from abc import ABC, abstractmethod

class QueueStreamRepository(ABC):
    """
    Port defining the interface for QueueStream persistence operations.
    """

    @abstractmethod
    def get_by_id(self, queue_stream_id: str) -> Optional[QueueStream]:
        pass

    @abstractmethod
    def save(self, queue_stream: QueueStream) -> None:
        """Persist a stream; assign a generated ID to the instance when new."""
        pass

    @abstractmethod
    def delete(self, queue_stream_id: str) -> None:
        pass

    @abstractmethod
    def remove(self, queue_stream_id: str, include_deleted: bool = False) -> None:
        """Permanently remove a stream from the storage backend."""
        pass

    @abstractmethod
    def get_all(self, include_deleted: bool = False) -> List[QueueStream]:
        pass
