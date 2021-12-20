from datetime import datetime
from enums.VideoSourceType import VideoSourceType

class VideoSource:
    def __init__(self, name: str = None, 
                url: str = None, 
                directory: str = None, 
                isWebSource: bool = None, 
                videoSourceType: VideoSourceType = None, 
                enableFetch: bool = None, 
                lastFetched: datetime = None, 
                datetimeAdded: datetime = None):
        self.name: str = name
        self.url: str = url
        self.directory: str = directory
        self.isWebSource: bool = isWebSource
        self.videoSourceType: VideoSourceType = videoSourceType
        self.enableFetch: bool = enableFetch
        self.lastFetched: datetime = lastFetched
        self.datetimeAdded: datetime = datetimeAdded