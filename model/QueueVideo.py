from datetime import datetime
import uuid

class QueueVideo:
    def __init__(self, 
                 videoName: str = None, 
                 uri: str = None, 
                 isWeb: bool = False, 
                 watched: datetime = None, 
                 datetimeAdded: datetime = datetime.now(), 
                 videoSourceId: str = None,
                 id: str = str(uuid.uuid4())):
        self.videoName: str = videoName
        self.uri: str = uri
        self.isWeb: bool = isWeb
        self.watched: datetime = watched
        self.datetimeAdded: datetime = datetimeAdded
        self.videoSourceId: str = videoSourceId
        self.id: str = id