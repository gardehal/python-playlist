from typing import Optional
from ports.playlist_repository import PlaylistRepository
from ports.queue_stream_repository import QueueStreamRepository
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from forms.YoutubePlaylistForm import YoutubePlaylistForm

class CreatePlaylistFromYoutubeUseCase:
    """
    Use Case to create a new Playlist from a YouTube URL.
    """

    def __init__(self, 
                 playlist_repository: PlaylistRepository, 
                 queue_stream_repository: QueueStreamRepository) -> None:
        self._playlist_repository = playlist_repository
        self._queue_stream_repository = queue_stream_repository

    def execute(self, url: str, name: Optional[str] = None, 
                description: Optional[str] = None, 
                play_watched_streams: bool = False, 
                allow_duplicates: bool = False, 
                favorite: bool = False, 
                sort_order: int = 0) -> Playlist:
        """
        Executes the logic to create a playlist from a YouTube URL.
        Note: In a real implementation, this would involve calling an external service 
        to parse the YouTube URL and extract metadata. For now, we'll use the provided data.

        Returns:
            Playlist: The newly created playlist object.
        """
        # In a full implementation, you'd use a service to fetch info from the URL here.
        # For this Use Case, we assume the metadata is either passed or extracted.
        
        new_playlist = Playlist(
            name=name or "New YouTube Playlist",
            description=description or f"Playlist from {url}",
            playWatchedStreams=play_watched_streams,
            allowDuplicates=allow_duplicates,
            favorite=favorite,
            sortOrder=sort_order,
            lastWatchedIndex=0,
            streamSourceIds=[],
            streamIds=[]
        )
        
        # In the legacy server.py logic, playlistService.add 'addYouTubePlaylist(new_playlist, url)' was used.
        # We'll simulate that by saving the playlist and potentially adding metadata here.
        self._playlist_repository.save(new_playlist)
        return new_playlist
