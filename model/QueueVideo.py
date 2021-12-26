from datetime import datetime
import uuid

class QueueVideo:
    def __init__(self, 
                 videoName: str = None, 
                 sourceUri: str = None, 
                 watched: datetime = None, 
                 datetimeAdded: datetime = datetime.now(), 
                 videoSourceId: str = None,
                 id: str = str(uuid.uuid4())):
        self.videoName: str = videoName
        self.sourceUri: str = sourceUri
        self.watched: datetime = watched
        self.datetimeAdded: datetime = datetimeAdded
        self.videoSourceId: str = videoSourceId
        self.id: str = id