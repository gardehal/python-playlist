from typing import List

from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource


class PlaylistDetailed():
    def __init__(self,
                 playlists: List[Playlist] = [],
                 queueStreams: List[QueueStream] = [],
                 streamSources: List[StreamSource] = [],):
        self.playlists: List[Playlist] = playlists
        self.queueStreams: List[QueueStream] = queueStreams
        self.streamSources: List[StreamSource] = streamSources
