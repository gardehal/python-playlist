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
                 id: str = str(uuid.uuid4())):
        self.name: str = name
        self.streamIds: List[str] = streamIds
        self.lastUpdated: datetime = lastUpdated
        self.lastWatchedIndex: int = lastWatchedIndex
        self.playWatchedStreams: bool = playWatchedStreams
        self.allowDuplicates: bool = allowDuplicates
        self.streamSourceIds: List[str] = streamSourceIds
        self.id: str = id

    def summaryString(self):
        return "".join(map(str, ["Name: ", self.name, 
        ", ID: ", self.id, 
        ", Streams: ", len(self.streamIds),
        ", Sources: ", len(self.streamSourceIds)]))

    def detailsString(self):
        return "".join(map(str, ["name: ", self.name, 
        ", n streamIds: ", len(self.streamIds), 
        ", lastUpdated: ", self.lastUpdated, 
        ", lastWatchedIndex: ", self.lastWatchedIndex, 
        ", playWatchedStreams: ", self.playWatchedStreams, 
        ", allowDuplicates: ", self.allowDuplicates, 
        ", n streamSourceIds: ", len(self.streamSourceIds), 
        ", id: ", self.id]))