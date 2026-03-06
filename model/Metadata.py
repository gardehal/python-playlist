from datetime import datetime

class Metadata:
    def __init__(self):
        self.playlistCount: int = 0
        self.queueStreamCount: int = 0
        self.streamSourceCount: int = 0
        self.softDeleteCount: int = 0
        self.totalEntityCount: int = 0
        self.lastFetchPlaylistName: str = 0
        self.lastFetchPlaylistId: str = 0
        self.lastFetchCount: int = 0
        self.lastFetch: datetime = 0
        self.serverUpAt: datetime = 0
        