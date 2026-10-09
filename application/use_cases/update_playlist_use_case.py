from typing import Optional
from ports.playlist_repository import PlaylistRepository
from model.Playlist import Playlist
from exceptions.domain_exceptions import PlaylistNotFoundError

class UpdatePlaylistUseCase:
    """
    Use Case to update an existing playlist's metadata.
    """

    def __init__(self, playlist_repository: PlaylistRepository) -> None:
        self._playlist_repository = playlist_repository

    def execute(self, playlist_id: str, name: str, description: Optional[str] = None, 
                play_watched_streams: bool = True, allow_duplicates: bool = True, 
                favorite: bool = False, sort_order: int = 1) -> Playlist:
        """
        Executes the logic to update a playlist.

        Returns:
            Playlist: The updated playlist object.

        Raises:
            PlaylistNotFoundError: If the playlist doesn't exist.
        """
        playlist = self._playlist_repository.get_by_id(playlist_id)
        
        if not playlist:
            raise PlaylistNotFoundError(f"Playlist with ID {playlist_id} not found.")

        playlist.name = name
        playlist.description = description
        playlist.playWatchedStreams = play_watched_streams
        playlist.allowDuplicates = allow_duplicates
        playlist.favorite = favorite
        playlist.sortOrder = sort_order
        
        self._playlist_repository.save(playlist)
        return playlist
