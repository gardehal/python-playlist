import os

import validators
from dotenv import load_dotenv
from grdService.BaseService import BaseService

from enums.StreamSourceType import StreamSourceTypeUtil
from model.StreamSource import StreamSource

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

T = StreamSource

class StreamSourceService(BaseService[T]):

    def __init__(self):
        BaseService.__init__(self, T, DEBUG, os.path.join(LOCAL_STORAGE_PATH, "StreamSource"))

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
        