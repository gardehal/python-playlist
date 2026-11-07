from abc import ABC, abstractmethod
from typing import List, Optional
from model.Playlist import Playlist

class PlaylistRepository(ABC):
    """Interface for playlist data access."""

    @abstractmethod
    def get_by_id(self, playlist_id: str) -> Optional[Playlist]:
        """Retrieve a playlist by its unique identifier."""
        pass

    @abstractmethod
    def save(self, playlist: Playlist) -> None:
        """Persist a playlist; assign a generated ID to the instance when new."""
        pass

    @abstractmethod
    def delete(self, playlist_id: str) -> None:
        """Remove a playlist from the storage backend."""
        pass

    @abstractmethod
    def get_all(self) -> List[Playlist]:
        """Retrieve all available playlists."""
        pass
