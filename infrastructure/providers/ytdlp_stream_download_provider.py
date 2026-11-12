import os
import shutil
from typing import Optional
from urllib.parse import urlparse

import yt_dlp
from grdUtil.DateTimeUtil import getDateTimeAsNumber
from grdUtil.InputUtil import sanitize
from werkzeug.utils import secure_filename

from ports.stream_download_provider import StreamDownloadProvider
from Settings import Settings


class YtDlpStreamDownloadProvider(StreamDownloadProvider):
    def __init__(self, storage_path: Optional[str] = None) -> None:
        self._storage_path = storage_path

    def download_stream(
        self,
        uri: str,
        playlist_name: str,
        audio_only: bool = False,
    ) -> Optional[str]:
        storage_path = self._storage_path or Settings().localStoragePath
        if not storage_path:
            raise ValueError("Local storage path is not configured.")

        playlist_directory = secure_filename(playlist_name) or "playlist"
        output_directory = os.path.join(storage_path, "video", playlist_directory)
        os.makedirs(output_directory, exist_ok=True)

        options = {
            "format": "bestaudio/best" if audio_only else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 5,
            "fragment_retries": 5,
            "windowsfilenames": os.name == "nt",
        }

        host = urlparse(uri).hostname or ""
        if host == "youtube.com" or host.endswith(".youtube.com") or host == "youtu.be":
            node_path = shutil.which("node")
            if node_path:
                options["js_runtimes"] = {"node": {"path": node_path}}
            options["extractor_args"] = {
                "youtube": {
                    "player_client": ["android", "web", "ios", "tv", "mweb"],
                    "po_token": None,
                    "player_skip": ["configs"],
                }
            }

        with yt_dlp.YoutubeDL(options) as downloader:
            metadata = downloader.extract_info(uri, download=False)

        if not metadata:
            return None

        title = metadata.get("title") or "unknown_video"
        filename_stem = f"{getDateTimeAsNumber()}_{title}".replace(" ", "_").lower()
        filename_stem = sanitize(filename_stem.replace("_", " "), mode=1).replace(" ", "_")
        filename_stem = filename_stem.replace("%", "%%")
        options["outtmpl"] = os.path.join(output_directory, f"{filename_stem}.%(ext)s")

        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(uri, download=True)

        if not info:
            return None

        path = info.get("filepath")
        if path:
            return path

        for requested_download in info.get("requested_downloads") or []:
            path = requested_download.get("filepath") or requested_download.get("filename")
            if path:
                return path

        return info.get("_filename")
