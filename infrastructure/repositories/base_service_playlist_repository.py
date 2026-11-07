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
        return self._service.get(playlist_id)

    def save(self, playlist: Playlist) -> None:
        if playlist.id and self._service.exists(playlist.id):
            self._service.update(playlist)
        else:
            self._service.add(playlist)

    def delete(self, playlist_id: str) -> None:
        self._service.delete(playlist_id)

    def get_all(self) -> List[Playlist]:
        return self._service.getAll()
