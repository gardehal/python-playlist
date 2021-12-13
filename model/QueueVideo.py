from myutil import DateTimeObject
from model.VideoSource import VideoSource

class QueueVideo:
    def __init__(self, videoSource: VideoSource, source: str, datetimeAdded: DateTimeObject, watched: bool):
        self.videoSource: VideoSource = videoSource
        self.source: str = source
        self.datetimeAdded: DateTimeObject = datetimeAdded
        self.watched: bool = watched