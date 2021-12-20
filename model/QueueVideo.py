from datetime import datetime

class QueueVideo:
    def __init__(self, videoName: str, sourceUri: str, watched: bool, datetimeAdded: datetime, videoSourceName: str):
        self.videoName: str = videoName
        self.sourceUri: str = sourceUri
        self.watched: bool = watched
        self.datetimeAdded: datetime = datetimeAdded
        self.videoSourceName: str = videoSourceName