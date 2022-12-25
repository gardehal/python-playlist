from typing import List

from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource


class PlaylistDetailed():
    def __init__(self,
                 playlist: Playlist = None,
                 queueStreams: List[QueueStream] = List[QueueStream],
                 streamSources: List[StreamSource] = List[StreamSource],):
        self.playlist: Playlist = playlist
        self.queueStreams: List[QueueStream] = queueStreams
        self.streamSources: List[StreamSource] = streamSources
