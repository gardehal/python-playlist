from datetime import datetime
import uuid

class StreamSource:
    def __init__(self, 
                 name: str = None, 
                 uri: str = None, 
                 isWeb: bool = None,
                 streamSourceTypeId: int = None, 
                 enableFetch: bool = None, 
                 lastFetched: datetime = None, 
                 datetimeAdded: datetime = datetime.now(),
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.uri: str = uri
        self.isWeb: bool = isWeb
        self.streamSourceTypeId: int = streamSourceTypeId
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

    def detailsString(self, includeUri: bool = True, includeId: bool = True):
        _uriString = ", uri: " + self.uri if(includeUri) else ""
        _uidString = ", id: " + self.id if(includeId) else ""
        
        return "".join(map(str, ["name: ", self.name,
        _uriString,
        ", isWeb: ", self.isWeb,
        ", streamSourceTypeId: ", self.streamSourceTypeId,
        ", enableFetch: ", self.enableFetch,
        ", lastFetched: ", self.lastFetched,
        ", datetimeAdded: ", self.datetimeAdded,
        _uidString]))