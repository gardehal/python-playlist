from typing import Optional

from ports.stream_download_provider import StreamDownloadProvider


class LegacyDownloadServiceAdapter(StreamDownloadProvider):
    def download_stream(
        self,
        uri: str,
        playlist_name: str,
        audio_only: bool = False,
    ) -> Optional[str]:
        from services.DownloadService import DownloadService

        return DownloadService().download(
            uri,
            playlist_name,
            audioOnly=audio_only,
        )
