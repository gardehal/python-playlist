from typing import List
from model.QueueVideo import QueueVideo
from datetime import datetime
import uuid

class Playlist():
    def __init__(self, 
                 name: str = None, 
                 videos: List[QueueVideo] = None, 
                 videoSourceCollectionName: str = None, 
                 videoSourceCollectionId: uuid = None, 
                 lastUpdated: datetime = datetime.now, 
                 lastWatchedIndex: int = None,
                 id: uuid = uuid.uuid4()):
        self.name: str = name
        self.videos: List[QueueVideo] = videos
        self.videoSourceCollectionName: str = videoSourceCollectionName
        self.videoSourceCollectionId: str = videoSourceCollectionId
        self.lastUpdated: datetime = lastUpdated
        self.lastWatchedIndex: int = lastWatchedIndex
        self.id: uuid = id