from typing import Optional
from ports.playlist_repository import PlaylistRepository
from model.Playlist import Playlist

class CreatePlaylistUseCase:
    """
    Use Case to create a new empty playlist.
    """

    def __init__(self, playlist_repository: PlaylistRepository) -> None:
        self._playlist_repository = playlist_repository

    def execute(self, name: str, description: Optional[str] = None, 
                play_watched_streams: bool = True, allow_duplicates: bool = True, 
                favorite: bool = False, sort_order: int = 1) -> Playlist:
        """
        Executes the logic to create a new playlist.

        Returns:
            Playlist: The newly created playlist object.
        """
        new_playlist = Playlist(
            name=name,
            description=description,
            playWatchedStreams=play_watched_streams,
            allowDuplicates=allow_duplicates,
            favorite=favorite,
            sortOrder=sort_order,
            last_watched_index=0,
            stream_source_ids=[],
            stream_ids=[]
        )
        
        self._playlist_repository.save(new_playlist)
        return new_playlist

