import os

import validators
from dotenv import load_dotenv
from grdService.BaseService import BaseService
from grdUtil.FileUtil import mkdir

from model.QueueStream import QueueStream

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

T = QueueStream

class QueueStreamService(BaseService[T]):

    def __init__(self):
        BaseService.__init__(self, T, DEBUG, os.path.join(LOCAL_STORAGE_PATH, "QueueStream"))

        mkdir(self.storagePath)

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
        