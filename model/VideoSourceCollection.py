import datetime
from typing import List
import uuid
from model.VideoSource import VideoSource

class VideoSourceCollection:
    def __init__(self, 
                 name: str = None, 
                 sources: List[VideoSource] = List[VideoSource], 
                 lastUpdated: datetime.datetime = datetime.datetime,
                 id: uuid = uuid.uuid4()):
        self.name: str = name
        self.sources: List[VideoSource] = sources
        self.lastUpdated: datetime.datetime = lastUpdated
        self.id: uuid = id