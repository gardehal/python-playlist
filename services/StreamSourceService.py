import os

import validators
from enums.StreamSourceType import StreamSourceTypeUtil
from grdService.BaseService import BaseService
from model.StreamSource import StreamSource
from Settings import Settings

T = StreamSource

class StreamSourceService(BaseService[T]):
    settings: Settings = None

    def __init__(self):
        self.settings = Settings()
        BaseService.__init__(self, T, self.settings.debug, os.path.join(self.settings.localStoragePath, "StreamSource"))

    def add(self, streamSource: T) -> T:
        """
        Add a new streamSource.

        Args:
            streamSource (StreamSource): streamSource to add

        Returns:
            StreamSource | None: returns StreamSource if success, else None
        """

        entity = streamSource
        entity.isWeb = validators.url(entity.uri)
        entity.streamSourceTypeId = StreamSourceTypeUtil.strToStreamSourceType(entity.uri).value
        
        return BaseService.add(self, entity)
        