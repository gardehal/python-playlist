from typing import Optional
from ports.playlist_repository import PlaylistRepository
from model.Playlist import Playlist
from exceptions.domain_exceptions import PlaylistNotFoundError, DuplicateStreamError

class AddStreamToPlaylistUseCase:
    """
    Use Case to add a new stream ID to an existing playlist.
    """

    def __init__(self, playlist_repository: PlaylistRepository) -> None:
        self._playlist_repository = playlist_repository

    def execute(self, playlist_id: str, stream_id: str) -> Playlist:
        """
        Executes the logic to add a stream to a playlist.
        
        Args:
            playlist_id (str): The ID of the playlist to update.
            stream_id (str): The ID of the stream to add.

        Returns:
            Playlist: The updated playlist object.

        Raises:
            PlaylistNotFoundError: If the playlist doesn't exist.
            DuplicateStreamError: If the stream is already in the playlist.
        """
        playlist = self._playlist_repository.get_by_id(playlist_id)
        
        if not playlist:
            raise PlaylistNotFoundError(f"Playlist with ID {playlist_id} not found.")

        if stream_id in playlist.streamIds:
            raise DuplicateStreamError(f"Stream {stream_id} is already in playlist '{playlist.name}'.")

        # Update the domain object
        playlist.streamIds.append(stream_id)
        
        # Persist via the repository port
        self._playlist_repository.save(playlist)
        
        return playlist
