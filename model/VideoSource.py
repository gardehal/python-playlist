from myutil import DateTimeObject

class VideoSource:
    def __init__(self, name: str, url: str, directory: str, isWebSource: bool, enableFetch: bool, lastFetched: DateTimeObject, datetimeAdded: DateTimeObject):
        self.name: str = name
        self.url: str = url
        self.directory: str = directory
        self.isWebSource: bool = isWebSource
        self.enableFetch: bool = enableFetch
        self.lastFetched: DateTimeObject = lastFetched
        self.datetimeAdded: DateTimeObject = datetimeAdded