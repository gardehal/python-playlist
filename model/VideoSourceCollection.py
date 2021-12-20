import datetime
from typing import List
from model.VideoSource import VideoSource

class VideoSourceCollection:
    def __init__(self, 
                 name: str = None, 
                 sources: List[VideoSource] = None, 
                 lastUpdated: datetime = None):
        self.name: str = name
        self.sources: List[VideoSource] = sources
        self.lastUpdated: datetime = lastUpdated