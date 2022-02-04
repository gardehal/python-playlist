from datetime import datetime
import uuid

class QueueStream:
    def __init__(self, 
                 name: str = None, 
                 uri: str = None, 
                 isWeb: bool = False, 
                 streamSourceId: str = None, 
                 watched: datetime = None, 
                 backgroundContent: bool = False, 
                 deleted: datetime = None,
                 added: datetime = datetime.now(),
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.uri: str = uri
        self.isWeb: bool = isWeb
        self.streamSourceId: str = streamSourceId
        self.watched: datetime = watched
        self.backgroundContent: bool = backgroundContent
        self.deleted: datetime = deleted
        self.added: datetime = added
        self.id: str = id

    def summaryString(self):
        return "".join(map(str, ["Name: ", self.name, 
        ", ID: ", self.id, 
        ", URI: ", self.uri]))

    def simpleString(self):
        return "".join(map(str, ["\"", self.name, "\"",
        ", watched" if(self.watched) else "",
        ", is web" if(self.isWeb) else ""]))

    def detailsString(self, includeUri: bool = True, includeId: bool = True, includeDatetime: bool = True, includeListCount: bool = True):
        _uriString = ", uri: " + self.uri if(includeUri) else ""
        _streamSourceIdString = ", streamSourceId: " + str(self.streamSourceId) if(includeId) else ""
        _idString = ", id: " + self.id if(includeId) else ""
        _watchedString = ", watched: " + str(self.watched) if(includeDatetime) else ""
        _deletedString = ", deleted: " + str(self.deleted) if(includeDatetime) else ""
        _addedString = ", added: " + str(self.added) if(includeDatetime) else ""
        
        return "".join(map(str, ["name: ", self.name,
        _uriString,
        ", isWeb: ", self.isWeb, 
        _streamSourceIdString,
        _watchedString, 
        ", backgroundContent: ", self.backgroundContent, 
        _deletedString,
        _addedString,
        _idString]))