import os
from typing import List, Optional
from grdService.BaseService import BaseService
from ports.queue_stream_repository import QueueStreamRepository
from model.QueueStream import QueueStream
from Settings import Settings

class BaseServiceQueueStreamRepository(QueueStreamRepository):
    """
    A concrete implementation of QueueStreamRepository that wraps the existing BaseService logic.
    """

    def __init__(self) -> None:
        self.settings = Settings()
        storage_path = os.path.join(self.settings.localStoragePath, "QueueStream")
        self._service = BaseService(QueueStream, self.settings.debug, storage_path)

    def get_by_id(self, queue_stream_id: str) -> Optional[QueueStream]:
        return self._service.get(queue_stream_id)

    def save(self, queue_stream: QueueStream) -> None:
        if queue_stream.id and self._service.exists(queue_stream.id):
            self._service.update(queue_stream)
        else:
            self._service.add(queue_stream)

    def delete(self, queue_stream_id: str) -> None:
        self._service.delete(queue_stream_id)

    def get_all(self) -> List[QueueStream]:
        return self._service.getAll()
