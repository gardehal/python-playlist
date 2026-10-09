from typing import List
from ports.playlist_repository import PlaylistRepository
from model.Playlist import Playlist

class GetAllPlaylistsUseCase:
    """
    Use Case to retrieve all playlists, sorted by their default order.
    """

    def __init__(self, playlist_repository: PlaylistRepository) -> None:
        self._playlist_repository = playlist_repository

    def execute(self) -> List[Playlist]:
        """
        Executes the logic to get all playlists sorted.

        Returns:
            List[Playlist]: A list of all playlists.
        """
        return self._playlist_repository.getAllSorted()
