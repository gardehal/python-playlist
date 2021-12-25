from datetime import datetime
from typing import List
import uuid

class VideoSourceCollection:
    def __init__(self, 
                 name: str = None, 
                 videoSourceIds: List[str] = List[str], 
                 lastUpdated: datetime = datetime.now,
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.videoSourceIds: List[str] = videoSourceIds
        self.lastUpdated: datetime = lastUpdated
        self.id: str = id