from datetime import datetime
import uuid

class StreamSource:
    def __init__(self, 
                 name: str = None, 
                 uri: str = None, 
                 isWeb: bool = None,
                 videoSourceTypeId: int = None, 
                 enableFetch: bool = None, 
                 lastFetched: datetime = None, 
                 datetimeAdded: datetime = datetime.now(),
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.uri: str = uri
        self.isWeb: bool = isWeb
        self.videoSourceTypeId: int = videoSourceTypeId
        self.enableFetch: bool = enableFetch
        self.lastFetched: datetime = lastFetched
        self.datetimeAdded: datetime = datetimeAdded
        self.id: str = id

    def summaryString(self):
        return "".join(map(str, ["Name: ", self.name, 
        ", ID: ", self.id, 
        ", URI: ", self.uri,
        ", Enable fetch: ", self.enableFetch,
        ", Last fetch: ", self.lastFetched]))

    def detailsString(self):
        return "".join(map(str, ["name: ", self.name, 
        ", uri: ", self.uri, 
        ", isWeb: ", self.isWeb,
        ", videoSourceTypeId: ", self.videoSourceTypeId,
        ", enableFetch: ", self.enableFetch,
        ", lastFetched: ", self.lastFetched,
        ", datetimeAdded: ", self.datetimeAdded,
        ", id: ", self.id]))