import unittest
import io
import os
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from mutagen.id3 import ID3

from application.use_cases.create_queue_stream_use_case import CreateQueueStreamUseCase
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from ports.stream_download_provider import AudioDownloadMetadata
from infrastructure.providers.youtube_provider import YoutubeProvider
from infrastructure.providers.ytdlp_stream_download_provider import YtDlpStreamDownloadProvider


class QueueStreamNamingTests(unittest.TestCase):
    def test_blank_web_name_uses_provider_metadata(self):
        saved = []
        requested = []
        repository = SimpleNamespace(save=saved.append)
        provider = SimpleNamespace(fetch_metadata=lambda uri: requested.append(uri) or {"name": " Video title "})
        use_case = CreateQueueStreamUseCase(repository, provider)

        stream = use_case.execute(" ", "https://example.com/video", False)

        self.assertEqual(stream.name, "Video title")
        self.assertEqual(requested, ["https://example.com/video"])
        self.assertEqual(saved, [stream])

    def test_manual_name_does_not_fetch_metadata(self):
        repository = SimpleNamespace(save=lambda stream: None)
        provider = SimpleNamespace(fetch_metadata=lambda uri: self.fail("Unexpected metadata lookup"))
        stream = CreateQueueStreamUseCase(repository, provider).execute(
            " Manual name ", "https://example.com/video", True
        )
        self.assertEqual(stream.name, "Manual name")

    def test_missing_metadata_does_not_save(self):
        saved = []
        repository = SimpleNamespace(save=saved.append)
        provider = SimpleNamespace(fetch_metadata=lambda uri: {})
        with self.assertRaises(ValueError):
            CreateQueueStreamUseCase(repository, provider).execute("", "https://example.com/video", True)
        self.assertEqual(saved, [])

    def test_youtube_metadata_title_is_used_and_missing_title_is_rejected(self):
        class FakeYoutubeDL:
            title = "YouTube video"

            def __init__(self, options):
                pass

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def extract_info(self, uri, download):
                if self.title is None:
                    return {}
                return {"title": self.title}

        saved = []
        use_case = CreateQueueStreamUseCase(SimpleNamespace(save=saved.append), YoutubeProvider())
        with patch("infrastructure.providers.youtube_provider.yt_dlp.YoutubeDL", FakeYoutubeDL):
            stream = use_case.execute("", "https://youtube.com/watch?v=video123", True)
            self.assertEqual(stream.name, "YouTube video")
            FakeYoutubeDL.title = None
            with self.assertRaises(ValueError):
                use_case.execute("", "https://youtube.com/watch?v=video456", True)

        self.assertEqual(saved, [stream])

    def test_metadata_extraction_failure_does_not_save(self):
        saved = []

        def fail(uri):
            raise RuntimeError("Network failure")

        use_case = CreateQueueStreamUseCase(
            SimpleNamespace(save=saved.append), SimpleNamespace(fetch_metadata=fail)
        )
        with self.assertRaisesRegex(ValueError, "Could not determine"):
            use_case.execute("", "https://youtube.com/watch?v=video123", True)
        self.assertEqual(saved, [])

    def test_local_path_uses_basename(self):
        repository = SimpleNamespace(save=lambda stream: None)
        stream = CreateQueueStreamUseCase(repository).execute("", r"C:\media\video.mp4", False)
        self.assertEqual(stream.name, "video.mp4")

    def test_web_create_displays_name_lookup_error(self):
        import server

        server.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        playlist = SimpleNamespace(id="playlist-naming")
        repository = SimpleNamespace(save=lambda stream: self.fail("Unexpected save"))
        provider = SimpleNamespace(fetch_metadata=lambda uri: {})
        use_case = CreateQueueStreamUseCase(repository, provider)
        with patch.object(server, "getPlaylistUseCase", SimpleNamespace(execute=lambda playlist_id: playlist)), \
             patch.object(server, "createQueueStreamUseCase", use_case):
            with server.app.test_client() as client:
                response = client.post("/queueStreams/create/playlist-naming", data={
                    "name": "", "uri": "https://example.com/video", "isWeb": "y"
                })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"detectable title", response.data)

    def test_web_create_fetches_title_and_links_the_saved_stream(self):
        import server

        server.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        playlist = SimpleNamespace(id="playlist-naming")
        saved = []
        linked = []

        def save(stream):
            stream.id = "stream-naming"
            saved.append(stream)

        use_case = CreateQueueStreamUseCase(
            SimpleNamespace(save=save),
            SimpleNamespace(fetch_metadata=lambda uri: {"name": "Fetched video"}),
        )
        with patch.object(server, "getPlaylistUseCase", SimpleNamespace(execute=lambda playlist_id: playlist)), \
             patch.object(server, "createQueueStreamUseCase", use_case), \
             patch.object(server, "addStreamToPlaylistUseCase", SimpleNamespace(execute=lambda *args: linked.append(args))), \
             patch.object(server, "playlistsDetails", return_value="created"):
            with server.app.test_client() as client:
                response = client.post("/queueStreams/create/playlist-naming", data={
                    "name": "", "uri": "https://youtube.com/watch?v=video123", "isWeb": "y"
                })

        self.assertEqual(response.data, b"created")
        self.assertEqual(saved[0].name, "Fetched video")
        self.assertEqual(linked, [("playlist-naming", "stream-naming")])

    def test_playlist_details_renders_audio_metadata_modal(self):
        import server

        server.app.config.update(TESTING=True)
        playlist = Playlist(
            name="Playlist Album",
            streamIds=["stream-1"],
            streamSourceIds=[],
            id="playlist-audio",
        )
        stream = QueueStream(
            name="Song",
            uri="https://youtube.com/watch?v=song123",
            streamSourceName="Source Artist",
            isWeb=True,
            id="stream-1",
        )
        details = SimpleNamespace(playlist=playlist, queue_streams=[stream], stream_sources=[])
        with patch.object(server, "getPlaylistDetailsUseCase", SimpleNamespace(execute=lambda playlist_id: details)):
            with server.app.test_client() as client:
                response = client.get(f"/playlists/{playlist.id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="fetch-playlist"', response.data)
        self.assertIn(b"Playlist fetch started.", response.data)
        self.assertIn(b"Fetch completed:", response.data)
        self.assertIn(b"Download audio (MP3)", response.data)
        self.assertIn(b"audio-download-trigger", response.data)
        self.assertIn(b"audio-download-modal-content", response.data)
        self.assertIn(b'name="album" type="text" value="Playlist Album"', response.data)
        self.assertIn(b'name="artist" type="text" value="Source Artist"', response.data)
        self.assertIn(b'name="year" type="number"', response.data)
        self.assertIn(b'name="genre" type="text"', response.data)


class DownloadNamingTests(unittest.TestCase):
    def test_thumbnail_saves_once_with_stable_cover_name(self):
        with tempfile.TemporaryDirectory(dir="tests") as output_directory:
            with patch(
                "infrastructure.providers.ytdlp_stream_download_provider.urlopen",
                return_value=io.BytesIO(b"image-data"),
            ) as urlopen_mock:
                first_path = YtDlpStreamDownloadProvider._save_thumbnail(
                    "https://i.ytimg.com/playlist.jpg", output_directory, "cover-playlist"
                )
                second_path = YtDlpStreamDownloadProvider._save_thumbnail(
                    "https://i.ytimg.com/other.jpg", output_directory, "cover-playlist"
                )

            with open(first_path, "rb") as image_file:
                image_data = image_file.read()

        self.assertEqual(os.path.basename(first_path), "cover-playlist.jpg")
        self.assertEqual(second_path, first_path)
        self.assertEqual(image_data, b"image-data")
        urlopen_mock.assert_called_once()

    def test_thumbnail_download_rejects_non_youtube_and_non_https_urls(self):
        with tempfile.TemporaryDirectory(dir="tests") as output_directory:
            with patch("infrastructure.providers.ytdlp_stream_download_provider.urlopen") as urlopen_mock:
                http_path = YtDlpStreamDownloadProvider._save_thumbnail(
                    "http://i.ytimg.com/playlist.jpg", output_directory, "cover-playlist"
                )
                external_path = YtDlpStreamDownloadProvider._save_thumbnail(
                    "https://example.com/playlist.jpg", output_directory, "cover-playlist"
                )
                malformed_path = YtDlpStreamDownloadProvider._save_thumbnail(
                    "https://i.ytimg.com:invalid/playlist.jpg", output_directory, "cover-playlist"
                )

        self.assertIsNone(http_path)
        self.assertIsNone(external_path)
        self.assertIsNone(malformed_path)
        urlopen_mock.assert_not_called()

    def test_audio_download_writes_user_metadata_and_track_number_to_id3(self):
        class FakeYoutubeDL:
            def __init__(self, options):
                self.options = dict(options)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def extract_info(self, uri, download):
                if not download:
                    return {"title": "Extractor title"}

                path = self.options["outtmpl"].replace("%(ext)s", "mp3")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb"):
                    pass
                return {"filepath": path}

        metadata = AudioDownloadMetadata(
            title="A Song: Original Title",
            album="Album Name",
            artist="Artist Name",
            year="2022",
            genre="Jazz",
            track_number=2,
            track_total=8,
        )
        with tempfile.TemporaryDirectory(dir="tests") as storage_path:
            with patch("infrastructure.providers.ytdlp_stream_download_provider.yt_dlp.YoutubeDL", FakeYoutubeDL), \
                 patch("infrastructure.providers.ytdlp_stream_download_provider.getDateTimeAsNumber", return_value=20261111123456):
                path = YtDlpStreamDownloadProvider(storage_path).download_stream(
                    "https://example.com/song",
                    "Playlist",
                    audio_only=True,
                    metadata=metadata,
                )

            tags = ID3(path)

        self.assertIn("Album_Name", path)
        self.assertEqual(tags["TIT2"].text[0], metadata.title)
        self.assertEqual(tags["TALB"].text[0], metadata.album)
        self.assertEqual(tags["TPE1"].text[0], metadata.artist)
        self.assertEqual(str(tags["TDRC"].text[0]), metadata.year)
        self.assertEqual(tags["TCON"].text[0], metadata.genre)
        self.assertEqual(tags["TRCK"].text[0], "2/8")

    def test_video_and_audio_filenames_include_timestamp_and_sanitized_title(self):
        class FakeYoutubeDL:
            calls = []

            def __init__(self, options):
                self.options = dict(options)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def extract_info(self, uri, download):
                self.calls.append((self.options, uri, download))
                if not download:
                    return {"title": "My Video: Episode 1"}
                extension = "mp3" if self.options.get("postprocessors") else "mp4"
                return {"filepath": self.options["outtmpl"].replace("%(ext)s", extension)}

        with tempfile.TemporaryDirectory(dir="tests") as storage_path:
            provider = YtDlpStreamDownloadProvider(storage_path)
            with patch("infrastructure.providers.ytdlp_stream_download_provider.yt_dlp.YoutubeDL", FakeYoutubeDL), \
                 patch("infrastructure.providers.ytdlp_stream_download_provider.getDateTimeAsNumber", return_value=20261111123456):
                video_path = provider.download_stream("https://example.com/video", "Playlist")
                audio_path = provider.download_stream("https://example.com/video", "Playlist", audio_only=True)

        video_name = os.path.basename(video_path)
        self.assertTrue(video_name.startswith("20261111123456_"))
        self.assertEqual(video_name, video_name.lower())
        self.assertNotIn(" ", video_name)
        self.assertNotIn(":", video_name)
        self.assertTrue(video_name.endswith(".mp4"))
        self.assertTrue(audio_path.endswith(".mp3"))
        self.assertEqual([call[2] for call in FakeYoutubeDL.calls], [False, True, False, True])