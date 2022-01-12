from datetime import datetime
import uuid

class QueueStream:
    def __init__(self, 
                 name: str = None, 
                 uri: str = None, 
                 isWeb: bool = False, 
                 watched: datetime = None, 
                 datetimeAdded: datetime = datetime.now(),
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.uri: str = uri
        self.isWeb: bool = isWeb
        self.watched: datetime = watched
        self.datetimeAdded: datetime = datetimeAdded
        self.id: str = id

    def summaryString(self):
        return "".join(map(str, ["Name: ", self.name, 
        ", ID: ", self.id, 
        ", URI: ", self.uri]))

    def detailsString(self, includeUri: bool = True, includeId: bool = True, includeDatetime: bool = True, includeListCount: bool = True):
        _uriString = ", uri: " + self.uri if(includeUri) else ""
        _idString = ", id: " + self.id if(includeId) else ""
        _watchedString = ", watched: " + self.watched if(includeDatetime) else ""
        _datetimeAddedString = ", datetimeAdded: " + self.datetimeAdded if(includeDatetime) else ""
        
        return "".join(map(str, ["name: ", self.name,
        _uriString,
        ", isWeb: ", self.isWeb, 
        _watchedString, 
        _datetimeAddedString,
        _idString]))