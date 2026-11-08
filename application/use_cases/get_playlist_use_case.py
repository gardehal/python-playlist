from typing import Optional

from model.Playlist import Playlist
from ports.playlist_repository import PlaylistRepository


class GetPlaylistUseCase:
    def __init__(self, playlist_repository: PlaylistRepository) -> None:
        self._playlist_repository = playlist_repository

    def execute(self, playlist_id: str) -> Optional[Playlist]:
        return self._playlist_repository.get_by_id(playlist_id)
