from typing import NamedTuple, Optional
from urllib.parse import parse_qs, urlparse

from model.QueueStream import QueueStream


class QueueStreamPlaybackUrls(NamedTuple):
    embedded_url: Optional[str]
    circumvent_url: Optional[str]


class GetQueueStreamPlaybackUrlsUseCase:
    def execute(self, queue_stream: QueueStream) -> QueueStreamPlaybackUrls:
        uri = queue_stream.uri or ""
        parsed_uri = urlparse(uri)
        host = parsed_uri.hostname.lower() if parsed_uri.hostname else ""
        path_parts = [part for part in parsed_uri.path.split("/") if part]
        is_youtube = (
            host == "youtu.be"
            or host == "youtube.com"
            or host.endswith(".youtube.com")
            or host == "youtube-nocookie.com"
            or host.endswith(".youtube-nocookie.com")
        )
        is_odysee = host == "odysee.com" or host.endswith(".odysee.com")

        youtube_id = queue_stream.remoteId
        if not youtube_id and is_youtube:
            video_ids = parse_qs(parsed_uri.query).get("v", [])
            if video_ids:
                youtube_id = video_ids[0]
            elif host == "youtu.be" and path_parts:
                youtube_id = path_parts[0]
            elif len(path_parts) > 1 and path_parts[0] in {"shorts", "embed", "live", "v"}:
                youtube_id = path_parts[1]

        embedded_url = None
        if is_youtube and youtube_id:
            embedded_url = f"https://www.youtube.com/embed/{youtube_id}"
        elif is_odysee and path_parts:
            embedded_url = f"https://odysee.com/$/embed/{'/'.join(path_parts)}"

        circumvent_url = None
        if queue_stream.isWeb and is_youtube and youtube_id:
            circumvent_url = f"https://www.nsfwyoutube.com/watch?v={youtube_id}"

        return QueueStreamPlaybackUrls(embedded_url, circumvent_url)
