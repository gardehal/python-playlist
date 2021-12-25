from datetime import datetime
import uuid

class QueueVideo:
    def __init__(self, 
                 videoName: str = None, 
                 sourceUri: str = None, 
                 watched: datetime = None, 
                 datetimeAdded: datetime = datetime.now, 
                 videoSourceName: str = None,
                 id: str = str(uuid.uuid4())):
        self.videoName: str = videoName
        self.sourceUri: str = sourceUri
        self.watched: datetime = watched
        self.datetimeAdded: datetime = datetimeAdded
        self.videoSourceName: str = videoSourceName
        self.id: str = id