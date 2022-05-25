from typing import List
from datetime import datetime

class Playlist():
    def __init__(self, 
                 name: str = None,
                 streamIds: List[str] = List[str], 
                 lastWatchedIndex: int = None,
                 playWatchedStreams: bool = True,
                 allowDuplicates: bool = True,
                 streamSourceIds: List[str] = List[str],
                 description: str = None,
                 deleted: datetime = None,
                 updated: datetime = datetime.now(),
                 added: datetime = datetime.now(),
                 id: str = None):
        self.name: str = name
        self.streamIds: List[str] = streamIds
        self.lastWatchedIndex: int = lastWatchedIndex
        self.playWatchedStreams: bool = playWatchedStreams
        self.allowDuplicates: bool = allowDuplicates
        self.streamSourceIds: List[str] = streamSourceIds
        self.description: str = description
        self.deleted: str = deleted
        self.updated: datetime = updated
        self.added: datetime = added
        self.id: str = id

    def summaryString(self):
        return "".join(map(str, ["Name: ", self.name, 
        ", ID: ", self.id, 
        ", Streams: ", len(self.streamIds),
        ", Sources: ", len(self.streamSourceIds)]))

    def simpleString(self):
        return "".join(map(str, ["\"", self.name, "\"",
        ", ", len(self.streamIds), " StreamSources",
        ", ", len(self.streamSourceIds), " SourceSources",]))

    def detailsString(self, includeUri: bool = True, includeId: bool = True, includeDatetime: bool = True, includeListCount: bool = True):
        idString = ", id: " + self.id if(includeId) else ""
        deletedString = ", deleted: " + str(self.deleted) if(includeDatetime) else ""
        updatedString = ", updated: " + str(self.updated) if(includeDatetime) else ""
        addedString = ", added: " + str(self.added) if(includeDatetime) else ""
        lenStreamString = ", n streamIds: " + str(len(self.streamIds)) if(includeListCount) else ""
        lenStreamStreamString = ", n streamSourceIds: " + str(len(self.streamIds)) if(includeListCount) else ""
        
        return "".join(map(str, ["name: ", self.name, 
        lenStreamString, 
        ", lastWatchedIndex: ", self.lastWatchedIndex, 
        ", playWatchedStreams: ", self.playWatchedStreams, 
        ", allowDuplicates: ", self.allowDuplicates, 
        lenStreamStreamString,
        ", description: ", self.description,
        deletedString,
        updatedString, 
        addedString,
        idString]))