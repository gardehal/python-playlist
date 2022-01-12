from typing import List
from datetime import datetime
import uuid

class Playlist():
    def __init__(self, 
                 name: str = None,
                 streamIds: List[str] = List[str], 
                 lastUpdated: datetime = datetime.now(), 
                 lastWatchedIndex: int = None,
                 playWatchedStreams: bool = True,
                 allowDuplicates: bool = True,
                 streamSourceIds: List[str] = List[str],
                 description: str = None,
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.streamIds: List[str] = streamIds
        self.lastUpdated: datetime = lastUpdated
        self.lastWatchedIndex: int = lastWatchedIndex
        self.playWatchedStreams: bool = playWatchedStreams
        self.allowDuplicates: bool = allowDuplicates
        self.streamSourceIds: List[str] = streamSourceIds
        self.description: str = description
        self.id: str = id

    def summaryString(self):
        return "".join(map(str, ["Name: ", self.name, 
        ", ID: ", self.id, 
        ", Streams: ", len(self.streamIds),
        ", Sources: ", len(self.streamSourceIds)]))

    def detailsString(self, includeUri: bool = True, includeId: bool = True, includeDatetime: bool = True, includeListCount: bool = True):
        _idString = ", id: " + self.id if(includeId) else ""
        _lastUpdatedString = ", lastUpdated: " + str(self.lastUpdated) if(includeDatetime) else ""
        _lenStreamString = ", n streamIds: " + len(self.streamIds) if(includeListCount) else ""
        _lenStreamStreamString = ", n streamSourceIds: " + len(self.streamIds) if(includeListCount) else ""
        
        return "".join(map(str, ["name: ", self.name, 
        _lenStreamString, 
        _lastUpdatedString, 
        ", lastWatchedIndex: ", self.lastWatchedIndex, 
        ", playWatchedStreams: ", self.playWatchedStreams, 
        ", allowDuplicates: ", self.allowDuplicates, 
        _lenStreamStreamString,
        ", description: ", self.description,
        _idString]))