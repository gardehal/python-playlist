from typing import List

from exceptions.domain_exceptions import PlaylistNotFoundError
from model.QueueStream import QueueStream
from ports.playlist_fetch_provider import PlaylistFetchProvider
from ports.playlist_repository import PlaylistRepository


class FetchPlaylistUseCase:
    def __init__(
        self,
        playlist_repository: PlaylistRepository,
        playlist_fetch_provider: PlaylistFetchProvider,
    ) -> None:
        self._playlist_repository = playlist_repository
        self._playlist_fetch_provider = playlist_fetch_provider

    def execute(
        self,
        playlist_id: str,
        batch_size: int,
        take_new_only: bool = True,
    ) -> List[QueueStream]:
        if self._playlist_repository.get_by_id(playlist_id) is None:
            raise PlaylistNotFoundError(f"Playlist with ID {playlist_id} not found.")

        return self._playlist_fetch_provider.fetch_playlist(
            playlist_id,
            batch_size,
            take_new_only,
        )
