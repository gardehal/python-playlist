from typing import List, Optional
from ports.playlist_repository import PlaylistRepository
from ports.queue_stream_repository import QueueStreamRepository
from ports.stream_source_repository import StreamSourceRepository
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource

class PlaylistDetailsDTO:
    def __init__(self, playlist: Playlist, queue_streams: List[QueueStream], stream_sources: List[StreamSource]):
        self.playlist = playlist
        self.queue_streams = queue_streams
        self.stream_sources = stream_sources

class GetPlaylistDetailsUseCase:
    """
    Use Case to retrieve a playlist along with its associated streams and sources.
    """

    def __init__(self, 
                 playlist_repository: PlaylistRepository,
                 queue_stream_repository: QueueStreamRepository,
                 stream_source_repository: StreamSourceRepository) -> None:
        self._playlist_repository = playlist_repository
        self._queue_stream_repository = queue_stream_repository
        self._stream_source_repository = stream_source_repository

    def execute(self, playlist_id: str) -> Optional[PlaylistDetailsDTO]:
        """
        Executes the logic to get playlist details.

        Returns:
            Optional[PlaylistDetailsDTO]: The DTO containing all info, or None if playlist not found.
        """
        playlist = self._playlist_repository.get_by_id(playlist_id)
        if not playlist:
            return None
            
        # Using the repository methods to fetch related entities
        queue_streams = self._queue_stream_repository.get_by_playlist_id(playlist_id)
        stream_sources = self._stream_source_repository.get_by_playlist_id(playlist_id)
        
        return PlaylistDetailsDTO(
            playlist=playlist,
            queue_streams=queue_streams,
            stream_sources=stream_sources
        )
