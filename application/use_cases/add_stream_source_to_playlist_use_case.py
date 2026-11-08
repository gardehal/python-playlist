from exceptions.domain_exceptions import PlaylistNotFoundError
from model.Playlist import Playlist
from ports.playlist_repository import PlaylistRepository


class AddStreamSourceToPlaylistUseCase:
    def __init__(self, playlist_repository: PlaylistRepository) -> None:
        self._playlist_repository = playlist_repository

    def execute(self, playlist_id: str, stream_source_id: str) -> Playlist:
        playlist = self._playlist_repository.get_by_id(playlist_id)
        if playlist is None:
            raise PlaylistNotFoundError(f"Playlist with ID {playlist_id} not found.")

        playlist.streamSourceIds.append(stream_source_id)
        self._playlist_repository.save(playlist)
        return playlist
