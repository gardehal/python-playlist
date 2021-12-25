from typing import List
from datetime import datetime
import uuid

class Playlist():
    def __init__(self, 
                 name: str = None, 
                 queueVideoIds: List[str] = List[str], 
                 videoSourceCollectionId: str = None, 
                 lastUpdated: datetime = datetime.now(), 
                 lastWatchedIndex: int = None,
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.queueVideoIds: List[str] = queueVideoIds
        self.videoSourceCollectionId: str = videoSourceCollectionId
        self.lastUpdated: datetime = lastUpdated
        self.lastWatchedIndex: int = lastWatchedIndex
        self.id: str = id