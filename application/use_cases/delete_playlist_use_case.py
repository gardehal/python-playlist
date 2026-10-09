from typing import Optional
from ports.playlist_repository import PlaylistRepository
from exceptions.domain_exceptions import PlaylistNotFoundError

class DeletePlaylistUseCase:
    """
    Use Case to delete a playlist from the system.
    """

    def __init__(self, playlist_repository: PlaylistRepository) -> None:
        self._playlist_repository = playlist_repository

    def execute(self, playlist_id: str) -> None:
        """
        Executes the logic to delete a playlist.

        Raises:
            PlaylistNotFoundError: If the playlist doesn't exist.
        """
        playlist = self._playlist_repository.get_by_id(playlist_id)
        if not playlist:
            raise PlaylistNotFoundError(f"Playlist with ID {playlist_id} not found.")
            
        self._playlist_repository.delete(playlist_id)
