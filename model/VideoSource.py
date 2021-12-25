from datetime import datetime
import uuid

class VideoSource:
    def __init__(self, 
                 name: str = None, 
                 url: str = None, 
                 directory: str = None, 
                 isWebSource: bool = None, 
                 videoSourceTypeId: str = None, 
                 enableFetch: bool = None, 
                 lastFetched: datetime = None, 
                 datetimeAdded: datetime = datetime.now,
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.url: str = url
        self.directory: str = directory
        self.isWebSource: bool = isWebSource
        self.videoSourceTypeId: str = videoSourceTypeId
        self.enableFetch: bool = enableFetch
        self.lastFetched: datetime = lastFetched
        self.datetimeAdded: datetime = datetimeAdded
        self.id: str = id