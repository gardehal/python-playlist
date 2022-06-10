from datetime import datetime

from grdUtil.DateTimeUtil import getDateTime


class QueueStream:
    def __init__(self, 
                 name: str = None, 
                 uri: str = None, 
                 isWeb: bool = False, 
                 streamSourceId: str = None, 
                 watched: datetime = None, 
                 backgroundContent: bool = False, 
                 deleted: datetime = None,
                 added: datetime = getDateTime(),
                 id: str = None):
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
        uriString = ", uri: " + self.uri if(includeUri) else ""
        streamSourceIdString = ", streamSourceId: " + str(self.streamSourceId) if(includeId) else ""
        idString = ", id: " + self.id if(includeId) else ""
        watchedString = ", watched: " + str(self.watched) if(includeDatetime) else ""
        deletedString = ", deleted: " + str(self.deleted) if(includeDatetime) else ""
        addedString = ", added: " + str(self.added) if(includeDatetime) else ""
        
        return "".join(map(str, ["name: ", self.name,
        uriString,
        ", isWeb: ", self.isWeb, 
        streamSourceIdString,
        watchedString, 
        ", backgroundContent: ", self.backgroundContent, 
        deletedString,
        addedString,
        idString]))
