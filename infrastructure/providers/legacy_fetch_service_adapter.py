from typing import List

from model.QueueStream import QueueStream
from ports.playlist_fetch_provider import PlaylistFetchProvider


class LegacyFetchServiceAdapter(PlaylistFetchProvider):
    def fetch_playlist(
        self,
        playlist_id: str,
        batch_size: int,
        take_new_only: bool,
    ) -> List[QueueStream]:
        from services.FetchService import FetchService

        return FetchService().fetch(
            playlist_id,
            batch_size,
            takeNewOnly=take_new_only,
        )
