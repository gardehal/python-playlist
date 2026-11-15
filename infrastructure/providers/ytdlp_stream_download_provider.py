import os
import shutil
from typing import Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import yt_dlp
from grdUtil.DateTimeUtil import getDateTimeAsNumber
from grdUtil.InputUtil import sanitize
from mutagen.id3 import ID3, TALB, TCON, TDRC, TIT2, TPE1, TRCK
from werkzeug.utils import secure_filename

from ports.stream_download_provider import AudioDownloadMetadata, StreamDownloadProvider
from Settings import Settings


class YtDlpStreamDownloadProvider(StreamDownloadProvider):
    def __init__(self, storage_path: Optional[str] = None) -> None:
        self._storage_path = storage_path

    def validate_options(self, audio_only: bool = False) -> None:
        if audio_only and shutil.which("ffmpeg") is None:
            raise RuntimeError(
                "Audio-only MP3 downloads require FFmpeg. Install FFmpeg and ensure ffmpeg is on PATH."
            )

    def download_stream(
        self,
        uri: str,
        playlist_name: str,
        audio_only: bool = False,
        metadata: Optional[AudioDownloadMetadata] = None,
    ) -> Optional[str]:
        self.validate_options(audio_only)
        storage_path = self._storage_path or Settings().localStoragePath
        if not storage_path:
            raise ValueError("Local storage path is not configured.")

        album_name = metadata.album if audio_only and metadata and metadata.album else playlist_name
        playlist_directory = secure_filename(album_name) or "playlist"
        output_directory = os.path.join(storage_path, "video", playlist_directory)
        os.makedirs(output_directory, exist_ok=True)
        if audio_only and metadata:
            self._save_thumbnail(metadata.playlist_thumbnail_url, output_directory, "cover-playlist")
            self._save_thumbnail(metadata.video_thumbnail_url, output_directory, "cover-video")

        options = {
            "format": "bestaudio/best" if audio_only else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 5,
            "fragment_retries": 5,
            "windowsfilenames": os.name == "nt",
        }
        if audio_only:
            options["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

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
            extracted_metadata = downloader.extract_info(uri, download=False)

        if not extracted_metadata:
            return None

        source_title = extracted_metadata.get("title") or "unknown_video"
        title = metadata.title if audio_only and metadata and metadata.title else source_title
        if audio_only:
            filename_stem = f"{getDateTimeAsNumber()}_{secure_filename(title) or 'unknown_video'}"
        else:
            filename_stem = f"{getDateTimeAsNumber()}_{source_title}".replace(" ", "_").lower()
            filename_stem = sanitize(filename_stem.replace("_", " "), mode=1).replace(" ", "_")
        filename_stem = filename_stem.replace("%", "%%")
        output_extension = "mp3" if audio_only else "%(ext)s"
        options["outtmpl"] = os.path.join(output_directory, f"{filename_stem}.{output_extension}")

        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(uri, download=True)

        if not info:
            return None

        path = info.get("filepath")
        if not path:
            for requested_download in info.get("requested_downloads") or []:
                path = requested_download.get("filepath") or requested_download.get("filename")
                if path:
                    break
        path = path or info.get("_filename") or os.path.join(output_directory, f"{filename_stem}.{output_extension}")

        if audio_only and metadata:
            self._write_mp3_metadata(path, metadata)
        return path

    @staticmethod
    def _write_mp3_metadata(path: str, metadata: AudioDownloadMetadata) -> None:
        tags = ID3()
        tags.add(TIT2(encoding=3, text=metadata.title))
        if metadata.artist:
            tags.add(TPE1(encoding=3, text=metadata.artist))
        if metadata.album:
            tags.add(TALB(encoding=3, text=metadata.album))
        if metadata.year:
            tags.add(TDRC(encoding=3, text=metadata.year))
        if metadata.genre:
            tags.add(TCON(encoding=3, text=metadata.genre))
        tags.add(TRCK(encoding=3, text=f"{metadata.track_number}/{metadata.track_total}"))
        tags.save(path)

    @staticmethod
    def _save_thumbnail(url: Optional[str], output_directory: str, filename_stem: str) -> Optional[str]:
        if not url:
            return None

        try:
            parsed_url = urlparse(url)
            host = (parsed_url.hostname or "").lower()
            port = parsed_url.port
        except ValueError:
            return None

        if (
            parsed_url.scheme != "https"
            or (host != "ytimg.com" and not host.endswith(".ytimg.com"))
            or port not in (None, 443)
        ):
            return None

        extension = os.path.splitext(parsed_url.path)[1].lower()
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            extension = ".jpg"
        target_path = os.path.join(output_directory, f"{filename_stem}{extension}")
        for existing_name in os.listdir(output_directory):
            if existing_name.startswith(f"{filename_stem}."):
                return os.path.join(output_directory, existing_name)

        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=30) as response, open(target_path, "wb") as image_file:
                shutil.copyfileobj(response, image_file)
        except Exception:
            try:
                os.remove(target_path)
            except OSError:
                pass
            return None

        return target_path
