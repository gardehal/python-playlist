from ports.external_stream_provider import ExternalStreamProvider
from typing import Dict, Any
import yt_dlp

class YoutubeProvider(ExternalStreamProvider):
    """
    Concrete adapter that uses YouTube-</strong>specific logic to fetch metadata via yt_dlp.
    """

    def fetch_metadata(self, uri: str) -> Dict[str, Any]:
        """
        Fetches real metadata from a YouTube URL using yt_dlp.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'force_generic_extractor': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(uri, download=False)
            
            return {
                "name": info.get("title", "Unknown Title"),
                "uri": uri,
                "is_web": True,
                "duration_seconds": info.get("duration", 0),
                "description": info.get("description", ""),
                "thumbnail": info.get("thumbnail", "")
            }

    def download_stream(self, uri: str) -> bytes:
        """
        Downloads the stream content from a YouTube URL using yt_dlp.
        Note: This returns the raw audio/video bytes.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio/best',
            'noplaylist': True,
            'outtmpl': '%(tempname)s.%(ext)s',
        }

        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # We use a fixed template to know exactly where the file is
            # yt_dlp will use the directory and the template provided
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestaudio/best',
                'noplaylist': True,
                'outtmpl': os.path.join(tmpdir, 'stream.%(ext)s'),
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'android'],
                    }
                },
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([uri])
                
                # Find the file in the temp directory
                actual_file = None
                for filename in os.listdir(tmpdir):
                    if filename.startswith('stream.'):
                        actual_file = os.path.join(tmpdir, filename)
                        break
                
                if not actual_file:
                     raise Exception("yt_dlp downloaded the file but we couldn't locate it in the temp directory.")

                with open(actual_file, 'rb') as f:
                    content = f.read()
                
                return content
            except Exception as e:
                raise Exception(f"Failed to download stream from {uri}: {e}")




