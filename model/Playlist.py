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

    def prettyText(self):
        return "".join(map(str, ["Name: ", self.name, 
        ", ID: ", self.id, 
        ", Streams: ", len(self.streamIds), 
        ", Play watched: ", self.playWatchedStreams, 
        ", Allow duplicates: ", self.allowDuplicates, 
        ", Sources: ", len(self.streamSourceIds)]))