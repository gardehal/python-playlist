from myutil import DateTimeObject
from enums.VideoSourceType import VideoSourceType

class VideoSource:
    def __init__(self, name: str, url: str, directory: str, isWebSource: bool, videoSourceType: VideoSourceType, enableFetch: bool, lastFetched: DateTimeObject, datetimeAdded: DateTimeObject):
        self.name: str = name
        self.url: str = url
        self.directory: str = directory
        self.isWebSource: bool = isWebSource
        self.videoSourceType: VideoSourceType = videoSourceType
        self.enableFetch: bool = enableFetch
        self.lastFetched: DateTimeObject = lastFetched
        self.datetimeAdded: DateTimeObject = datetimeAdded