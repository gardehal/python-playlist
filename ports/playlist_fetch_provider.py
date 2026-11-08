from abc import ABC, abstractmethod
from typing import List

from model.QueueStream import QueueStream


class PlaylistFetchProvider(ABC):
    @abstractmethod
    def fetch_playlist(
        self,
        playlist_id: str,
        batch_size: int,
        take_new_only: bool,
    ) -> List[QueueStream]:
        pass
