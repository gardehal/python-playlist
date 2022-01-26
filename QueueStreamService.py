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
    storagePath: str = LOCAL_STORAGE_PATH
    queueStreamRepository: LocalJsonRepository = None

    def __init__(self):
        self.queueStreamRepository: str = LocalJsonRepository(T, DEBUG, os.path.join(self.storagePath, "QueueStream"))

        mkdir(self.storagePath)

    def add(self, queueStream: T) -> T:
        """
        Add a new QueueStream.

        Args:
            queueStream (QueueStream): QueueStream to add

        Returns:
            QueueStream | None: returns QueueStream if success, else None
        """

        _entity = queueStream
        _entity.isWeb = validators.url(_entity.uri)
        _entity.watched = None
        _entity.deleted = None
        _entity.added = datetime.now()
        _entity.id = str(uuid.uuid4())
        
        _result = self.queueStreamRepository.add(_entity)
        if(_result):
            return _entity
        else:
            return None

    def get(self, id: str, includeSoftDeleted: bool = False) -> T:
        """
        Get QueueStream by ID.

        Args:
            id (str): ID of QueueStream to get
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            QueueStream: QueueStream if any, else None
        """

        _entity = self.queueStreamRepository.get(id)
        
        if(_entity != None and _entity.deleted != None and not includeSoftDeleted):
            printS("DEBUG: get - QueueStream with ID ", _entity.id, " was soft deleted.", color=colors["WARNING"], doPrint = DEBUG)
            return None
        else:
            return _entity

    def getAll(self, includeSoftDeleted: bool = False) -> List[T]:
        """
        Get all QueueStreams.

        Args:
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[QueueStream]: list of QueueStreams
        """

        _entities = self.queueStreamRepository.getAll()
        _result = []
        
        for _entity in _entities:
            if(_entity.deleted != None and not includeSoftDeleted):
                printS("DEBUG: getAll - QueueStream with ID ", _entity.id, " was soft deleted.", color=colors["WARNING"], doPrint = DEBUG)
            else:
                _result.append(_entity)
            
        return _result
    
    def getAllIds(self, includeSoftDeleted: bool = False) -> List[str]:
        """
        Get all IDs of queueStreams.

        Args:
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[str]: queueStreams IDs if any, else empty list
        """
        
        _all = self.getAll(includeSoftDeleted)
        return [_.id for _ in _all]

    def update(self, queueStream: T) -> T:
        """
        Update QueueStream.

        Args:
            queueStream (QueueStream): queueStream to update

        Returns:
            QueueStream | None: returns QueueStream if success, else None
        """

        _entity = queueStream
        _entity.added = datetime.now()
        _result = self.queueStreamRepository.update(_entity)
        if(_result):
            return _entity
        else:
            return None

    def delete(self, id: str) -> T:
        """
        (Soft) Delete a QueueStream.

        Args:
            id (str): ID of QueueStream to delete

        Returns:
            QueueStream | None: returns QueueStream if success, else None
        """

        _entity = self.get(id)
        if(_entity == None):
            return None

        _entity.deleted = datetime.now()
        _result = self.update(_entity)
        if(_result):
            return _entity
        else:
            return None
        
    def restore(self, id: str) -> T:
        """
        Restore a (soft) deleted QueueStream.

        Args:
            id (str): ID of QueueStream to restore

        Returns:
            QueueStream | None: returns QueueStream if success, else None
        """

        _entity = self.get(id, includeSoftDeleted = True)
        if(_entity == None):
            return None

        _entity.deleted = None
        _result = self.update(_entity)
        if(_result):
            return _entity
        else:
            return None
        
    def remove(self, id: str, includeSoftDeleted: bool = False) -> T:
        """
        Permanently remove QueueStream.

        Args:
            id (str): ID of QueueStream to remove
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            QueueStream | None: returns QueueStream if success, else None
        """

        _entity = self.get(id, includeSoftDeleted)
        if(_entity == None):
            return None
        
        _result = self.queueStreamRepository.remove(_entity.id)
        if(_result):
            return _entity
        else:
            return None

    def addOrUpdate(self, queueStream: T) -> T:
        """
        Add queueStream if none exists, else update existing.

        Args:
            queueStream (T): queueStream to add or update

        Returns:
            QueueStream | None: returns QueueStream if success, else None
        """
        
        if(self.get(queueStream.id) == None):
            return self.add(queueStream)

        return self.update(queueStream)