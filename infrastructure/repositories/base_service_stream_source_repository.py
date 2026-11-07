import os
from typing import List, Optional
from grdService.BaseService import BaseService
from ports.stream_source_repository import StreamSourceRepository
from model.StreamSource import StreamSource
from Settings import Settings

class BaseServiceStreamSourceRepository(StreamSourceRepository):
    """
    A concrete implementation of StreamSourceRepository that wraps the existing BaseService logic.
    """

    def __init__(self) -> None:
        self.settings = Settings()
        storage_path = os.path.join(self.settings.localStoragePath, "StreamSource")
        self._service = BaseService(StreamSource, self.settings.debug, storage_path)

    def get_by_id(self, stream_source_id: str) -> Optional[StreamSource]:
        return self._service.get(stream_source_id)

    def save(self, stream_source: StreamSource) -> None:
        if stream_source.id and self._service.exists(stream_source.id):
            self._service.update(stream_source)
        else:
            self._service.add(stream_source)

    def delete(self, stream_source_id: str) -> None:
        self._service.delete(stream_source_id)

    def get_all(self) -> List[StreamSource]:
        return self._service.getAll()
