import os
import uuid
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from myutil.LocalJsonRepository import LocalJsonRepository
from enums.StreamSourceType import StreamSourceTypeUtil

from model.StreamSource import StreamSource

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

T = StreamSource

class StreamSourceService():
    debug: bool = DEBUG
    storagePath: str = LOCAL_STORAGE_PATH
    streamSourceRepository: LocalJsonRepository = None

    def __init__(self):
        self.streamSourceRepository: str = LocalJsonRepository(T, self.debug, os.path.join(self.storagePath, "StreamSource"))

    def add(self, streamSource: T) -> T:
        """
        Add a new streamSource.

        Args:
            streamSource (StreamSource): streamSource to add

        Returns:
            StreamSource | None: returns StreamSource if success, else None
        """

        _entity = streamSource
        _entity.id = str(uuid.uuid4())
        _entity.datetimeAdded = datetime.now()
        _entity.videoSourceTypeId = StreamSourceTypeUtil.strToStreamSourceType(_entity.uri)
        _result = self.streamSourceRepository.add(_entity)
        if(_result):
            return _entity
        else:
            return None

    def get(self, id: str) -> T:
        """
        Get streamSource by ID.

        Args:
            id (str): id of streamSource to get

        Returns:
            StreamSource: streamSource if any, else None
        """

        return self.streamSourceRepository.get(id)

    def getAll(self) -> List[T]:
        """
        Get all streamSources.

        Returns:
            List[StreamSource]: streamSources if any, else empty list
        """

        return self.streamSourceRepository.getAll()

    def getAllIds(self) -> List[str]:
        """
        Get all IDs of streamSources.

        Returns:
            List[str]: streamSources IDs if any, else empty list
        """
        
        _all = self.getAll()
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

    def remove(self, id: str) -> T:
        """
        Remove streamSource.

        Args:
            id (str): id of streamSource to remove

        Returns:
            StreamSource | None: returns StreamSource if success, else None
        """

        _entity = self.get(id)
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
            streamSource (T): streamSource to add or update

        Returns:
            StreamSource | None: returns StreamSource if success, else None
        """

        if(self.get(streamSource.id) == None):
            return self.add(streamSource)

        return self.update(streamSource)
