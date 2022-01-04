from datetime import datetime
import uuid
from myutil.LocalJsonRepository import LocalJsonRepository
from myutil.Util import *
from typing import List
from model.QueueStream import QueueStream
from dotenv import load_dotenv

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

T = QueueStream

class QueueStreamService():
    debug: bool = DEBUG
    storagePath: str = LOCAL_STORAGE_PATH
    queueStreamRepository: LocalJsonRepository = None

    def __init__(self):
        self.queueStreamRepository: str = LocalJsonRepository(T, self.debug, os.path.join(self.storagePath, "QueueStream"))

        mkdir(self.storagePath)

    def add(self, queueStream: T) -> T:
        """
        Add a new queueStream.

        Args:
            queueStream (QueueStream): queueStream to add

        Returns:
            QueueStream | None: returns added QueueStream if success, else None
        """

        _queueStream = queueStream
        _queueStream.id = str(uuid.uuid4())
        _queueStream.datetimeAdded = datetime.now()
        _result = self.queueStreamRepository.add(_queueStream)
        if(_result):
            return _queueStream
        else:
            return None

    def get(self, id: str) -> T:
        """
        Get queueStream by ID.

        Args:
            id (str): id of queueStream to get

        Returns:
            QueueStream: queueStream if any, else None
        """

        return self.queueStreamRepository.get(id)

    def getAll(self) -> List[T]:
        """
        Get all queueStreams.

        Returns:
            List[QueueStream]: queueStreams if any, else empty list
        """

        return self.queueStreamRepository.getAll()
    
    def getAllIds(self) -> List[str]:
        """
        Get all IDs of queueStreams.

        Returns:
            List[str]: queueStreams IDs if any, else empty list
        """
        
        _all = self.getAll()
        return [_.id for _ in _all]

    def update(self, queueStream: T) -> bool:
        """
        Update QueueStream.

        Args:
            queueStream (QueueStream): queueStream to update

        Returns:
            bool: success = True
        """

        queueStream.datetimeAdded = datetime.now()
        return self.queueStreamRepository.update(queueStream)

    def remove(self, id: str) -> bool:
        """
        Remove queueStream.

        Args:
            id (str): id of queueStream to remove

        Returns:
            bool: success = True
        """

        return self.queueStreamRepository.remove(id)

    def addOrUpdate(self, queueStream: T) -> bool:
        """
        Add queueStream if none exists, else update existing.

        Args:
            queueStream (T): queueStream to add or update

        Returns:
            bool: success = True
        """

        if(self.add(queueStream) != None):
            return True

        return self.update(queueStream)