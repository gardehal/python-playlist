from datetime import datetime
from typing import List

from grdUtil.DateTimeUtil import getDateTime


class StreamSource:
    def __init__(self, 
                 name: str = None,
                 uri: str = None,
                 isWeb: bool = None,
                 streamSourceTypeId: int = 0,
                 enableFetch: bool = None,
                 lastFetched: datetime = None,
                 lastSuccessfulFetched: datetime = None,
                 lastFetchedId: str = None, # Legacy
                 lastFetchedIds: List[str] = [],
                 backgroundContent: bool = False,
                 alwaysDownload: bool = False,
                 deleted: datetime = None,
                 added: datetime = getDateTime(),
                 id: str = None):
        self.name: str = name
        self.uri: str = uri
        self.isWeb: bool = isWeb
        self.streamSourceTypeId: int = streamSourceTypeId
        self.enableFetch: bool = enableFetch
        self.lastFetched: datetime = lastFetched
        self.lastSuccessfulFetched: datetime = lastSuccessfulFetched
        self.lastFetchedIds: List[str] = lastFetchedIds
        self.backgroundContent: bool = backgroundContent
        self.alwaysDownload: bool = alwaysDownload
        self.deleted: datetime = deleted
        self.added: datetime = added
        self.id: str = id

    def summaryString(self):
        return "".join(map(str, ["Name: ", self.name, 
        ", ID: ", self.id, 
        ", URI: ", self.uri,
        ", Enable fetch: ", self.enableFetch,
        ", Last fetch: ", self.lastSuccessfulFetched]))

    def simpleString(self):
        return "".join(map(str, ["\"", self.name, "\"",
        ", fetch enabled" if(self.enableFetch) else "",
        ", is web" if(self.isWeb) else "",
        ", Last fetch: ", self.lastSuccessfulFetched]))

    def detailsString(self, includeUri: bool = True, includeId: bool = True, includeDatetime: bool = True, includeListCount: bool = True):
        uriString = ", uri: " + self.uri if(includeUri) else ""
        idString = ", id: " + self.id if(includeId) else ""
        lastFetchedIdsString = ", lastFetchedIds: " + str(self.lastFetchedIds) if(includeId) else ""
        lastFetchedString = ", lastFetched: " + str(self.lastFetched) if(includeDatetime) else ""
        lastSuccessfulFetchedString = ", lastSuccessfulFetched: " + str(self.lastSuccessfulFetched) if(includeDatetime) else ""
        deletedString = ", deleted: " + str(self.deleted) if(includeDatetime) else ""
        addedString = ", added: " + str(self.added) if(includeDatetime) else ""
        
        return "".join(map(str, ["\"", self.name, "\"",
        uriString,
        # ", isWeb: ", self.isWeb,
        # ", streamSourceTypeId: ", self.streamSourceTypeId,
        ", fetch: ", self.enableFetch,
        lastFetchedString,
        lastSuccessfulFetchedString,
        lastFetchedIdsString,
        # ", backgroundContent: ", self.backgroundContent, 
        deletedString,
        addedString,
        idString]))
