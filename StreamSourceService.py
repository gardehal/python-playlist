from datetime import datetime
from LocalJsonRepository import LocalJsonRepository
from myutil.Util import *
from typing import List
from model.StreamSource import StreamSource
from dotenv import load_dotenv

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

        mkdir(self.storagePath)

    def add(self, streamSource: T) -> bool:
        """
        Add a new streamSource.

        Args:
            streamSource (StreamSource): streamSource to add

        Returns:
            bool: success = True
        """

        streamSource.datetimeAdded = datetime.now()
        return self.streamSourceRepository.add(streamSource)

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

        if(self.add(streamSource)):
            return True

        return self.update(streamSource)