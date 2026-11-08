from abc import ABC, abstractmethod
from typing import Optional


class StreamDownloadProvider(ABC):
    @abstractmethod
    def download_stream(
        self,
        uri: str,
        playlist_name: str,
        audio_only: bool = False,
    ) -> Optional[str]:
        pass
