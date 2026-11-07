from typing import List

from model.StreamSource import StreamSource
from ports.stream_source_repository import StreamSourceRepository

class GetAllStreamSourcesUseCase:
    def __init__(self, stream_source_repository: StreamSourceRepository):
        self._stream_source_repository = stream_source_repository

    def execute(self) -> List[StreamSource]:
        return self._stream_source_repository.get_all()
