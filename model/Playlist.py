from typing import List
from model.VideoSource import VideoSource
from model.QueueVideo import QueueVideo
from datetime import datetime

class Playlist():
    def __init__(self, 
                 name: str = None, 
                 videos: List[QueueVideo] = None, 
                 videoSource: VideoSource = None, 
                 lastUpdated: datetime = None, 
                 lastWatchedIndex: int = None):
        self.name: str = name
        self.videos: List[QueueVideo] = videos
        self.videoSource: VideoSource = videoSource
        self.lastUpdated: datetime = lastUpdated
        self.lastWatchedIndex: int = lastWatchedIndex