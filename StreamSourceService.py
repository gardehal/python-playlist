import os
import uuid
from datetime import datetime
from typing import List

import validators
from dotenv import load_dotenv
from myutil.BashColor import BashColor
from myutil.LocalJsonRepository import LocalJsonRepository
from myutil.PrintUtil import printS

from enums.StreamSourceType import StreamSourceTypeUtil
from model.StreamSource import StreamSource

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

T = StreamSource

class StreamSourceService():
    storagePath: str = LOCAL_STORAGE_PATH
    streamSourceRepository: LocalJsonRepository = None

    def __init__(self):
        self.streamSourceRepository: str = LocalJsonRepository(T, DEBUG, os.path.join(self.storagePath, "StreamSource"))

    def add(self, streamSource: T) -> T:
        """
        Add a new streamSource.

        Args:
            streamSource (StreamSource): streamSource to add

        Returns:
            StreamSource | None: returns StreamSource if success, else None
        """

        _entity = streamSource
        _entity.isWeb = validators.url(_entity.uri)
        _entity.streamSourceTypeId = StreamSourceTypeUtil.strToStreamSourceType(_entity.uri).value
        _entity.deleted = None
        _entity.added = datetime.now()
        _entity.id = str(uuid.uuid4())
        
        _result = self.streamSourceRepository.add(_entity)
        if(_result):
            return _entity
        else:
            return None

    def get(self, id: str, includeSoftDeleted: bool = False) -> T:
        """
        Get StreamSource by ID.

        Args:
            id (str): ID of StreamSource to get
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            StreamSource: StreamSource if any, else None
        """

        _entity = self.streamSourceRepository.get(id)
        
        if(_entity != None and _entity.deleted != None and not includeSoftDeleted):
            printS("DEBUG: get - StreamSource with ID ", _entity.id, " was soft deleted.", color  =BashColor.WARNING, doPrint = DEBUG)
            return None
        else:
            return _entity

    def getAll(self, includeSoftDeleted: bool = False) -> List[T]:
        """
        Get all StreamSources.

        Args:
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[StreamSource]: list of StreamSources
        """

        _entities = self.streamSourceRepository.getAll()
        _result = []
        
        for _entity in _entities:
            if(_entity.deleted != None and not includeSoftDeleted):
                printS("DEBUG: getAll - StreamSource with ID ", _entity.id, " was soft deleted.", color = BashColor.WARNING, doPrint = DEBUG)
            else:
                _result.append(_entity)
            
        return _result

    def getAllIds(self, includeSoftDeleted: bool = False) -> List[str]:
        """
        Get all IDs of streamSources.

        Args:
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[str]: streamSources IDs if any, else empty list
        """

        _all = self.getAll(includeSoftDeleted)
        return [_.id for _ in _all]

    def update(self, streamSource: T) -> T:
        """
        Update StreamSource.

        Args:
            streamSource (StreamSource): streamSource to update

        Returns:
            StreamSource | None: returns StreamSource if success, else None
        """

        _entity = streamSource
        _result = self.streamSourceRepository.update(_entity)
        if(_result):
            return _entity
        else:
            return None

    def delete(self, id: str) -> T:
        """
        (Soft) Delete a StreamSource.

        Args:
            id (str): ID of StreamSource to delete

        Returns:
            StreamSource | None: returns StreamSource if success, else None
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
        Restore a (soft) deleted StreamSource.

        Args:
            id (str): ID of StreamSource to restore

        Returns:
            StreamSource | None: returns StreamSource if success, else None
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
        Permanently remove a StreamSource.

        Args:
            id (str): ID of StreamSource to remove
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            StreamSource | None: returns StreamSource if success, else None
        """

        _entity = self.get(id, includeSoftDeleted)
        if(_entity == None):
            return None

        _result = self.streamSourceRepository.remove(_entity.id)
        if(_result):
            return _entity
        else:
            return None

    def addOrUpdate(self, streamSource: T) -> T:
        """
        Add streamSource if none exists, else update existing.

        Args:
            streamSource (StreamSource): StreamSource to add or update

        Returns:
            StreamSource | None: returns StreamSource if success, else None
        """

        if(self.get(streamSource.id) == None):
            return self.add(streamSource)

        return self.update(streamSource)
