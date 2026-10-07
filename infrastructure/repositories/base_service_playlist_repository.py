import os
from typing import List, Optional
from grdService.BaseService import BaseService
from ports.playlist_repository import PlaylistRepository
from model.Playlist import Playlist
from Settings import Settings

class BaseServicePlaylistRepository(PlaylistRepository):
    """
    A concrete implementation of PlaylistRepository that wraps the existing BaseService logic.
    This allows us to use the established file-system persistence while adhering to the new Port interface.
    """

    def __init__(self) -> None:
        self.settings = Settings()
        # We wrap the existing BaseService logic here.
        # The storage path is constructed just like in the original services.
        storage_path = os.path.join(self.settings.localStoragePath, "Playlist")
        self._service = BaseService(Playlist, self.settings.debug, storage_path)

    def get_by_id(self, playlist_id: str) -> Optional[Playlist]:
        """Retrieve a playlist by its unique identifier using BaseService."""
        # We use the existing 'exists' and retrieval logic from BaseService via entityRepository
        if self._service.exists(playlist_id):
            # Since BaseService uses LocalJsonRepository, we can access the underlying repository
            return self._service.entityRepository.getById(playlist_id)
        return None

    def save(self, playlist: Playlist) -> None:
        """Persist a playlist using BaseService's add method."""
        self._service.add(playlist)

    def delete(self, playlist_id: str) -> None:
        """Remove a playlist using the underlying repository."""
        # Assuming BaseService/LocalJsonRepository has a delete or similar mechanism
        # If not explicitly in BaseService snippet, we use the entityRepository directly
        self._service.entityRepository.delete(playlist_id)

    def get_all(self) -> List[Playlist]:
        """Retrieve all available playlists."""
        return self._service.entityRepository.getAll()
