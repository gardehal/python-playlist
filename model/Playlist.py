from typing import List
from model.VideoSource import VideoSource
from model.QueueVideo import QueueVideo
from datetime import datetime

class Playlist():
    def __init__(self, name: str videos: List[QueueVideo], videoSource: VideoSource, lastUpdated: datetime, lastWatchedIndex: int):
        self.name: str = name
        self.videoSource: VideoSource = videoSource
        self.videos: List[QueueVideo] = videos
        self.lastUpdated: datetime = lastUpdated
        self.lastWatchedIndex: int = lastWatchedIndex