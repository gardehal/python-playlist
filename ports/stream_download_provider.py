from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AudioDownloadMetadata:
    title: str
    album: str
    artist: Optional[str]
    year: Optional[str]
    genre: Optional[str]
    track_number: int
    track_total: int
    playlist_thumbnail_url: Optional[str] = None
    video_thumbnail_url: Optional[str] = None


class StreamDownloadProvider(ABC):
    @abstractmethod
    def validate_options(self, audio_only: bool = False) -> None:
        """Raise an actionable error when the requested download mode is unavailable."""
        pass

    @abstractmethod
    def download_stream(
        self,
        uri: str,
        playlist_name: str,
        audio_only: bool = False,
        metadata: Optional[AudioDownloadMetadata] = None,
    ) -> Optional[str]:
        pass
