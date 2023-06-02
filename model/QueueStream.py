from datetime import datetime

from grdUtil.StrUtil import maxLen
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
                 remoteId: str = None,
                 id: str = None):
        self.name: str = name
        self.uri: str = uri
        self.isWeb: bool = isWeb
        self.streamSourceId: str = streamSourceId
        self.watched: datetime = watched
        self.backgroundContent: bool = backgroundContent
        self.deleted: datetime = deleted
        self.added: datetime = added
        self.remoteId: str = remoteId
        self.id: str = id
        
    def default(self):
        self.name: str = "name"
        self.uri: str = "uri"
        self.isWeb: bool = False
        self.streamSourceId: str = "streamSourceId"
        self.watched: datetime = getDateTime()
        self.backgroundContent: bool = False
        self.deleted: datetime = datetime.now()
        self.added: datetime = getDateTime()
        self.remoteId: str = "remoteId"
        self.id: str = "id"
        return self

    def summaryString(self):
        return "".join(map(str, ["Name: ", self.name, 
        ", ID: ", self.id, 
        ", URI: ", self.uri]))

    def simpleString(self):
        return "".join(map(str, ["\"", self.name, "\"",
        ", watched" if(self.watched) else "",
        ", is web" if(self.isWeb) else ""]))

    def shortString(self):
        return "".join(map(str, ["\"", maxLen(self.name, 40), "\""]))

    def watchedString(self):
        return "".join(map(str, [self.id,
        ", watched: " + str(self.watched)[0:20] if(self.watched) else "",
        " - \"", maxLen(self.name, 20), "\" - "]))

    def detailsString(self, includeUri: bool = True, includeId: bool = True, includeDatetime: bool = True, includeListCount: bool = True):
        uriString = ", uri: " + self.uri if(includeUri) else ""
        streamSourceIdString = ", streamSourceId: " + str(self.streamSourceId) if(includeId) else ""
        idString = ", id: " + self.id if(includeId) else ""
        watchedString = ", watched: " + str(self.watched) if(includeDatetime) else ""
        deletedString = ", deleted: " + str(self.deleted) if(includeDatetime) else ""
        addedString = ", added: " + str(self.added) if(includeDatetime) else ""
        
        return "".join(map(str, ["name: ",  maxLen(self.name, 40),
        uriString,
        # ", isWeb: ", self.isWeb, 
        streamSourceIdString,
        watchedString, 
        # ", backgroundContent: ", self.backgroundContent, 
        deletedString,
        addedString,
        idString]))
