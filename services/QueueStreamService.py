import os

import validators
from grdService.BaseService import BaseService
from model.QueueStream import QueueStream
from Settings import Settings

T = QueueStream

class QueueStreamService(BaseService[T]):
    settings = Settings()

    def __init__(self):
        BaseService.__init__(self, T, self.settings.debug, os.path.join(self.settings.localStoragePath, "QueueStream"))

    def add(self, queueStream: T) -> T:
        """
        Add a new QueueStream.

        Args:
            queueStream (QueueStream): QueueStream to add

        Returns:
            QueueStream | None: returns QueueStream if success, else None
        """

        entity = queueStream
        entity.isWeb = validators.url(entity.uri)
        
        return BaseService.add(self, entity)
        