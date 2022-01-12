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
                 lastSuccessfulFetched: datetime = None, 
                 datetimeAdded: datetime = datetime.now(),
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.uri: str = uri
        self.isWeb: bool = isWeb
        self.streamSourceTypeId: int = streamSourceTypeId
        self.enableFetch: bool = enableFetch
        self.lastFetched: datetime = lastFetched
        self.lastSuccessfulFetched: datetime = lastSuccessfulFetched
        self.datetimeAdded: datetime = datetimeAdded
        self.id: str = id

    def summaryString(self):
        return "".join(map(str, ["Name: ", self.name, 
        ", ID: ", self.id, 
        ", URI: ", self.uri,
        ", Enable fetch: ", self.enableFetch,
        ", Last fetch: ", self.lastSuccessfulFetched]))

    def detailsString(self, includeUri: bool = True, includeId: bool = True, includeDatetime: bool = True, includeListCount: bool = True):
        _uriString = ", uri: " + self.uri if(includeUri) else ""
        _idString = ", id: " + self.id if(includeId) else ""
        _lastFetchedString = ", lastFetched: " + str(self.lastFetched) if(includeDatetime) else ""
        _lastSuccessfulFetchedString = ", lastSuccessfulFetched: " + str(self.lastSuccessfulFetched) if(includeDatetime) else ""
        _datetimeAddedString = ", datetimeAdded: " + str(self.datetimeAdded) if(includeDatetime) else ""
        
        return "".join(map(str, ["name: ", self.name,
        _uriString,
        ", isWeb: ", self.isWeb,
        ", streamSourceTypeId: ", self.streamSourceTypeId,
        ", enableFetch: ", self.enableFetch,
        _lastFetchedString,
        _lastSuccessfulFetchedString,
        _datetimeAddedString,
        _idString]))