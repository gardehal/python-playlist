from datetime import datetime

class QueueVideo:
    def __init__(self, 
                 videoName: str = None, 
                 sourceUri: str = None, 
                 watched: datetime = None, 
                 datetimeAdded: datetime = None, 
                 videoSourceName: str = None):
        self.videoName: str = videoName
        self.sourceUri: str = sourceUri
        self.watched: datetime = watched
        self.datetimeAdded: datetime = datetimeAdded
        self.videoSourceName: str = videoSourceName