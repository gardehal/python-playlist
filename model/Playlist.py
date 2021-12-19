from typing import List
from VideoSource import VideoSource
from QueueVideo import QueueVideo
from myutil import DateTimeObject

class Playlist:
    def __init__(self, name: str videos: List(QueueVideo), videoSource: VideoSource, lastUpdated: DateTimeObject, lastWatchedIndex: int):
        self.name: str = name
        self.videoSource: VideoSource = videoSource
        self.videos: List(QueueVideo) = videos
        self.lastUpdated: DateTimeObject = lastUpdated
        self.lastWatchedIndex: int = lastWatchedIndex