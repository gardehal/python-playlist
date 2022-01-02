import os
import uuid
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from myutil.LocalJsonRepository import LocalJsonRepository

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
            StreamSource | None: returns added StreamSource if success, else None
        """
        
        _streamSource = streamSource
        _streamSource.id = str(uuid.uuid4())
        _streamSource.datetimeAdded = datetime.now()
        _result = self.streamSourceRepository.add(_streamSource)
        if(_result):
            return _streamSource
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

    def update(self, streamSource: T) -> bool:
        """
        Update StreamSource.

        Args:
            streamSource (StreamSource): streamSource to update

        Returns:
            bool: success = True
        """

        streamSource.datetimeAdded = datetime.now()
        return self.streamSourceRepository.update(streamSource)

    def remove(self, id: str) -> bool:
        """
        Remove streamSource.

        Args:
            id (str): id of streamSource to remove

        Returns:
            bool: success = True
        """

        return self.streamSourceRepository.remove(id)

    def addOrUpdate(self, streamSource: T) -> bool:
        """
        Add streamSource if none exists, else update existing.

        Args:
            streamSource (T): streamSource to add or update

        Returns:
            bool: success = True
        """

        if(self.add(streamSource) != None):
            return True

        return self.update(streamSource)
