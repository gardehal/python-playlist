import datetime
from typing import List
from model.VideoSource import VideoSource

class VideoSourceCollection:
    def __init__(self, name: str, sources: List[VideoSource], lastUpdated: datetime):
        self.name: str = name
        self.sources: List[VideoSource] = sources
        self.lastUpdated: datetime = lastUpdated