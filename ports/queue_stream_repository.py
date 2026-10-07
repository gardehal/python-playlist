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
        pass

    @abstractmethod
    def delete(self, queue_stream_id: str) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[QueueStream]:
        pass
