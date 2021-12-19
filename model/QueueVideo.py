from myutil import DateTimeObject

class QueueVideo:
    def __init__(self, videoName: str, sourceUri: str, watched: bool, datetimeAdded: DateTimeObject, videoSourceName: str):
        self.videoName: str = videoName
        self.sourceUri: str = sourceUri
        self.watched: bool = watched
        self.datetimeAdded: DateTimeObject = datetimeAdded
        self.videoSourceName: str = videoSourceName