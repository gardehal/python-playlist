import contextlib
import io
import unittest
from datetime import datetime
import tempfile
from unittest.mock import patch

from application.use_cases.add_stream_to_playlist_use_case import AddStreamToPlaylistUseCase
from application.use_cases.create_queue_stream_use_case import CreateQueueStreamUseCase
from application.use_cases.create_playlist_use_case import CreatePlaylistUseCase
from application.use_cases.create_playlist_from_youtube_use_case import CreatePlaylistFromYoutubeUseCase
from application.use_cases.create_stream_source_use_case import CreateStreamSourceUseCase
from application.use_cases.delete_queue_stream_use_case import DeleteQueueStreamUseCase
from application.use_cases.delete_playlist_use_case import DeletePlaylistUseCase
from application.use_cases.delete_stream_source_use_case import DeleteStreamSourceUseCase
from application.use_cases.get_all_playlists_use_case import GetAllPlaylistsUseCase
from application.use_cases.get_all_queue_streams_use_case import GetAllQueueStreamsUseCase
from application.use_cases.get_all_stream_sources_use_case import GetAllStreamSourcesUseCase
from application.use_cases.get_playlist_details_use_case import GetPlaylistDetailsUseCase
from application.use_cases.get_queue_stream_details_use_case import GetQueueStreamDetailsUseCase
from application.use_cases.get_stream_source_details_use_case import GetStreamSourceDetailsUseCase
from application.use_cases.toggle_queue_stream_watched_use_case import ToggleQueueStreamWatchedUseCase
from application.use_cases.update_playlist_use_case import UpdatePlaylistUseCase
from application.use_cases.update_queue_stream_use_case import UpdateQueueStreamUseCase
from application.use_cases.update_stream_source_use_case import UpdateStreamSourceUseCase
from exceptions.domain_exceptions import DuplicateStreamError, PlaylistNotFoundError, StreamSourceError
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource
from ports.playlist_repository import PlaylistRepository
from ports.queue_stream_repository import QueueStreamRepository
from ports.stream_source_repository import StreamSourceRepository
from infrastructure.providers.youtube_provider import YoutubeProvider
from infrastructure.repositories.base_service_playlist_repository import BaseServicePlaylistRepository
from infrastructure.repositories.base_service_queue_stream_repository import BaseServiceQueueStreamRepository
from infrastructure.repositories.base_service_stream_source_repository import BaseServiceStreamSourceRepository
from composition_root import CompositionRoot


class QueueStreamRepositoryStub(QueueStreamRepository):
    def __init__(self):
        self.queue_streams = {}
        self.saved = []
        self.deleted = []

    def get_by_id(self, queue_stream_id):
        return self.queue_streams.get(queue_stream_id)

    def save(self, queue_stream):
        if queue_stream.id is None:
            queue_stream.id = f"queue-stream-{len(self.saved) + 1}"
        self.queue_streams[queue_stream.id] = queue_stream
        self.saved.append(queue_stream)

    def delete(self, queue_stream_id):
        self.deleted.append(queue_stream_id)
        self.queue_streams.pop(queue_stream_id, None)

    def get_all(self):
        return list(self.queue_streams.values())


class StreamSourceRepositoryStub(StreamSourceRepository):
    def __init__(self):
        self.stream_sources = {}
        self.saved = []
        self.deleted = []

    def get_by_id(self, stream_source_id):
        return self.stream_sources.get(stream_source_id)

    def save(self, stream_source):
        self.saved.append(stream_source)

    def delete(self, stream_source_id):
        self.deleted.append(stream_source_id)
        self.stream_sources.pop(stream_source_id, None)

    def get_all(self):
        return list(self.stream_sources.values())


class PlaylistRepositoryStub(PlaylistRepository):
    def __init__(self):
        self.playlists = {}

    def get_by_id(self, playlist_id):
        return self.playlists.get(playlist_id)

    def save(self, playlist):
        if playlist.id is None:
            playlist.id = f"playlist-{len(self.playlists) + 1}"
        self.playlists[playlist.id] = playlist

    def delete(self, playlist_id):
        self.playlists.pop(playlist_id, None)

    def get_all(self):
        return list(self.playlists.values())


class QueueStreamUseCaseTests(unittest.TestCase):
    def setUp(self):
        self.repository = QueueStreamRepositoryStub()

    def test_create_saves_queue_stream_through_repository(self):
        use_case = CreateQueueStreamUseCase(self.repository)

        queue_stream = use_case.execute(
            name="Video",
            uri="https://example.com/video",
            is_web=True,
            stream_source_id="source-1",
            stream_source_name="Source",
        )

        self.assertIs(self.repository.saved[0], queue_stream)
        self.assertEqual(queue_stream.name, "Video")
        self.assertEqual(queue_stream.streamSourceId, "source-1")

    def test_create_preserves_optional_queue_stream_fields(self):
        use_case = CreateQueueStreamUseCase(self.repository)
        watched = datetime(2026, 1, 1)

        queue_stream = use_case.execute(
            name="Video",
            uri="https://youtube.com/watch?v=video123",
            is_web=True,
            watched=watched,
            background_content=True,
            playtime_seconds=240,
            remote_id="video123",
        )

        self.assertIs(queue_stream.watched, watched)
        self.assertTrue(queue_stream.backgroundContent)
        self.assertEqual(queue_stream.playtimeSeconds, 240)
        self.assertEqual(queue_stream.remoteId, "video123")
        self.assertTrue(queue_stream.thumbnailUrl.endswith("/video123/hqdefault.jpg"))

    def test_refactored_web_create_uses_case_and_links_saved_stream(self):
        import server_refactor

        server_refactor.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        playlist = Playlist(name="Web playlist", streamIds=[], id="playlist-web")
        playlist_repository = PlaylistRepositoryStub()
        playlist_repository.playlists[playlist.id] = playlist
        queue_stream_repository = QueueStreamRepositoryStub()
        server_refactor.playlistRepository = playlist_repository
        server_refactor.queueStreamRepository = queue_stream_repository
        server_refactor.createQueueStreamUseCase = CreateQueueStreamUseCase(queue_stream_repository)
        server_refactor.playlistsDetails = lambda playlist_id: "created"

        with server_refactor.app.test_client() as client:
            response = client.post("/queueStreams/create/playlist-web", data={
                "name": "Video",
                "uri": "https://www.youtube.com/watch?v=web123",
                "isWeb": "y",
                "watched": "y",
                "backgroundContent": "y",
                "playtimeSeconds": "320",
            })

        self.assertEqual(response.data, b"created")
        self.assertEqual(len(queue_stream_repository.saved), 1)
        queue_stream = queue_stream_repository.saved[0]
        self.assertTrue(queue_stream.isWeb)
        self.assertTrue(queue_stream.backgroundContent)
        self.assertEqual(queue_stream.playtimeSeconds, 320)
        self.assertEqual(queue_stream.remoteId, "web123")
        self.assertTrue(queue_stream.thumbnailUrl.endswith("/web123/hqdefault.jpg"))
        self.assertEqual(playlist.streamIds, [queue_stream.id])

    def test_refactored_web_edit_updates_queue_stream_through_case(self):
        import server_refactor

        server_refactor.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        queue_stream = QueueStream(
            name="Before",
            uri="https://example.com/before",
            streamSourceId="source-before",
            streamSourceName="Source before",
            id="queue-stream-edit",
        )
        repository = QueueStreamRepositoryStub()
        repository.queue_streams[queue_stream.id] = queue_stream
        server_refactor.getQueueStreamDetailsUseCase = GetQueueStreamDetailsUseCase(repository)
        server_refactor.updateQueueStreamUseCase = UpdateQueueStreamUseCase(repository)
        server_refactor.queueStreamsDetails = lambda queue_stream_id: "updated"

        with server_refactor.app.test_client() as client:
            response = client.post("/queueStreams/edit/queue-stream-edit", data={
                "name": "After",
                "uri": "https://youtube.com/watch?v=edit123",
                "isWeb": "y",
                "streamSourceId": "source-after",
                "streamSourceName": "Source after",
                "watched": "y",
                "backgroundContent": "y",
                "playtimeSeconds": "410",
                "remoteId": "edit123",
            })

        self.assertEqual(response.data, b"updated")
        self.assertEqual(queue_stream.name, "After")
        self.assertEqual(queue_stream.uri, "https://youtube.com/watch?v=edit123")
        self.assertTrue(queue_stream.isWeb)
        self.assertEqual(queue_stream.streamSourceId, "source-after")
        self.assertEqual(queue_stream.streamSourceName, "Source after")
        self.assertTrue(queue_stream.watched)
        self.assertTrue(queue_stream.backgroundContent)
        self.assertEqual(queue_stream.playtimeSeconds, 410)
        self.assertEqual(queue_stream.remoteId, "edit123")
        self.assertIs(repository.saved[-1], queue_stream)

    def test_update_changes_requested_fields_and_saves(self):
        existing = QueueStream(name="Before", uri="https://example.com/video", id="qs-1")
        self.repository.queue_streams["qs-1"] = existing
        use_case = UpdateQueueStreamUseCase(self.repository)

        result = use_case.execute("qs-1", name="After", is_web=True)

        self.assertIs(result, existing)
        self.assertEqual(existing.name, "After")
        self.assertEqual(existing.uri, "https://example.com/video")
        self.assertTrue(existing.isWeb)
        self.assertIs(self.repository.saved[-1], existing)

    def test_update_missing_queue_stream_raises_value_error(self):
        use_case = UpdateQueueStreamUseCase(self.repository)

        with self.assertRaisesRegex(ValueError, "qs-missing"):
            use_case.execute("qs-missing", name="After")

    def test_delete_delegates_to_repository(self):
        use_case = DeleteQueueStreamUseCase(self.repository)

        use_case.execute("qs-1")

        self.assertEqual(self.repository.deleted, ["qs-1"])


class ReadUseCaseTests(unittest.TestCase):
    def test_get_all_playlists_sorts_by_favorite_sort_order_and_name(self):
        repository = PlaylistRepositoryStub()
        playlists = [
            Playlist(name="Regular", favorite=False, sortOrder=1, id="regular"),
            Playlist(name="Favorite later", favorite=True, sortOrder=2, id="favorite-later"),
            Playlist(name="Favorite first", favorite=True, sortOrder=1, id="favorite-first"),
        ]
        for playlist in playlists:
            repository.playlists[playlist.id] = playlist

        result = GetAllPlaylistsUseCase(repository).execute()

        self.assertEqual([playlist.id for playlist in result], ["favorite-first", "favorite-later", "regular"])

    def test_get_all_queue_streams_returns_repository_values(self):
        repository = QueueStreamRepositoryStub()
        queue_stream = QueueStream(name="Video", id="qs-1")
        repository.queue_streams[queue_stream.id] = queue_stream

        self.assertEqual(GetAllQueueStreamsUseCase(repository).execute(), [queue_stream])

    def test_get_all_stream_sources_returns_repository_values(self):
        repository = StreamSourceRepositoryStub()
        stream_source = StreamSource(name="Channel", id="ss-1")
        repository.stream_sources[stream_source.id] = stream_source

        self.assertEqual(GetAllStreamSourcesUseCase(repository).execute(), [stream_source])

    def test_get_queue_stream_details_returns_entity_or_none(self):
        repository = QueueStreamRepositoryStub()
        queue_stream = QueueStream(name="Video", id="qs-1")
        repository.queue_streams[queue_stream.id] = queue_stream
        use_case = GetQueueStreamDetailsUseCase(repository)

        self.assertIs(use_case.execute("qs-1"), queue_stream)
        self.assertIsNone(use_case.execute("missing"))

    def test_get_stream_source_details_returns_entity_or_none(self):
        repository = StreamSourceRepositoryStub()
        stream_source = StreamSource(name="Channel", id="ss-1")
        repository.stream_sources[stream_source.id] = stream_source
        use_case = GetStreamSourceDetailsUseCase(repository)

        self.assertIs(use_case.execute("ss-1"), stream_source)
        self.assertIsNone(use_case.execute("missing"))


class StreamSourceUseCaseTests(unittest.TestCase):
    def setUp(self):
        self.repository = StreamSourceRepositoryStub()

    def test_create_saves_stream_source_through_repository(self):
        use_case = CreateStreamSourceUseCase(self.repository)

        source = use_case.execute(
            name="Channel",
            uri="https://example.com/channel",
            is_web=True,
            stream_source_type_id=2,
            enable_fetch=True,
        )

        self.assertIs(self.repository.saved[0], source)
        self.assertEqual(source.name, "Channel")
        self.assertEqual(source.streamSourceTypeId, 2)
        self.assertTrue(source.enableFetch)

    def test_update_changes_requested_fields_and_saves(self):
        existing = StreamSource(name="Before", uri="https://example.com/channel", id="ss-1")
        self.repository.stream_sources["ss-1"] = existing
        use_case = UpdateStreamSourceUseCase(self.repository)

        result = use_case.execute("ss-1", name="After", enable_fetch=False)

        self.assertIs(result, existing)
        self.assertEqual(existing.name, "After")
        self.assertEqual(existing.uri, "https://example.com/channel")
        self.assertFalse(existing.enableFetch)
        self.assertIs(self.repository.saved[-1], existing)

    def test_update_missing_stream_source_raises_domain_error(self):
        use_case = UpdateStreamSourceUseCase(self.repository)

        with self.assertRaisesRegex(StreamSourceError, "ss-missing"):
            use_case.execute("ss-missing", name="After")

    def test_delete_existing_stream_source_delegates_to_repository(self):
        self.repository.stream_sources["ss-1"] = StreamSource(id="ss-1")
        use_case = DeleteStreamSourceUseCase(self.repository)

        use_case.execute("ss-1")

        self.assertEqual(self.repository.deleted, ["ss-1"])

    def test_delete_missing_stream_source_raises_domain_error(self):
        use_case = DeleteStreamSourceUseCase(self.repository)

        with self.assertRaisesRegex(StreamSourceError, "ss-missing"):
            use_case.execute("ss-missing")


class PlaylistDetailsUseCaseTests(unittest.TestCase):
    def test_details_resolve_playlist_ids_in_order_and_skip_missing_entities(self):
        playlist_repository = PlaylistRepositoryStub()
        queue_stream_repository = QueueStreamRepositoryStub()
        stream_source_repository = StreamSourceRepositoryStub()
        playlist = Playlist(
            name="Test playlist",
            streamIds=["qs-2", "qs-1", "qs-missing"],
            streamSourceIds=["ss-1", "ss-missing"],
            id="playlist-1",
        )
        playlist_repository.playlists[playlist.id] = playlist
        queue_stream_repository.queue_streams["qs-1"] = QueueStream(name="First", id="qs-1")
        queue_stream_repository.queue_streams["qs-2"] = QueueStream(name="Second", id="qs-2")
        stream_source_repository.stream_sources["ss-1"] = StreamSource(name="Source", id="ss-1")
        use_case = GetPlaylistDetailsUseCase(
            playlist_repository,
            queue_stream_repository,
            stream_source_repository,
        )

        result = use_case.execute("playlist-1")

        self.assertIs(result.playlist, playlist)
        self.assertEqual([stream.id for stream in result.queue_streams], ["qs-2", "qs-1"])
        self.assertEqual([source.id for source in result.stream_sources], ["ss-1"])

    def test_missing_playlist_returns_none(self):
        use_case = GetPlaylistDetailsUseCase(
            PlaylistRepositoryStub(),
            QueueStreamRepositoryStub(),
            StreamSourceRepositoryStub(),
        )

        self.assertIsNone(use_case.execute("playlist-missing"))


class PlaylistLifecycleUseCaseTests(unittest.TestCase):
    def setUp(self):
        self.repository = PlaylistRepositoryStub()

    def test_create_saves_playlist_with_requested_settings(self):
        use_case = CreatePlaylistUseCase(self.repository)

        playlist = use_case.execute(
            name="Favorites",
            description="Saved videos",
            play_watched_streams=False,
            allow_duplicates=False,
            favorite=True,
            sort_order=3,
        )

        self.assertIs(self.repository.playlists[playlist.id], playlist)
        self.assertEqual(playlist.name, "Favorites")
        self.assertEqual(playlist.streamIds, [])
        self.assertEqual(playlist.streamSourceIds, [])

    def test_create_from_youtube_persists_playlist_and_video_streams(self):
        playlist_repository = PlaylistRepositoryStub()
        queue_stream_repository = QueueStreamRepositoryStub()
        provider = YoutubePlaylistProviderStub({
            "title": "Channel playlist",
            "entries": [
                {"id": "video-1", "title": "First video", "thumbnail": "https://thumbs.example/1.jpg"},
                {"id": "video-2", "title": "Second video"},
                {"title": "Entry without ID"},
            ],
        })
        use_case = CreatePlaylistFromYoutubeUseCase(
            playlist_repository,
            queue_stream_repository,
            provider,
        )

        playlist = use_case.execute("https://youtube.com/playlist?list=test")

        self.assertEqual(playlist.name, "Channel playlist")
        self.assertEqual(playlist.streamIds, ["queue-stream-1", "queue-stream-2"])
        self.assertEqual(len(queue_stream_repository.saved), 2)
        self.assertEqual(queue_stream_repository.saved[0].remoteId, "video-1")
        self.assertEqual(queue_stream_repository.saved[0].thumbnailUrl, "https://thumbs.example/1.jpg")
        self.assertEqual(queue_stream_repository.saved[1].thumbnailUrl, "https://i.ytimg.com/vi/video-2/hqdefault.jpg")

    def test_create_from_youtube_empty_playlist_saves_no_streams(self):
        playlist_repository = PlaylistRepositoryStub()
        queue_stream_repository = QueueStreamRepositoryStub()
        provider = YoutubePlaylistProviderStub({"title": "Empty playlist", "entries": []})
        use_case = CreatePlaylistFromYoutubeUseCase(
            playlist_repository,
            queue_stream_repository,
            provider,
        )

        playlist = use_case.execute("https://youtube.com/playlist?list=empty")

        self.assertEqual(playlist.name, "Empty playlist")
        self.assertEqual(playlist.streamIds, [])
        self.assertEqual(queue_stream_repository.saved, [])
        self.assertIs(playlist_repository.get_by_id(playlist.id), playlist)

    def test_create_from_youtube_provider_error_saves_nothing(self):
        class FailingProvider:
            def fetch_playlist(self, uri):
                raise RuntimeError("provider failed")

        playlist_repository = PlaylistRepositoryStub()
        queue_stream_repository = QueueStreamRepositoryStub()
        use_case = CreatePlaylistFromYoutubeUseCase(
            playlist_repository,
            queue_stream_repository,
            FailingProvider(),
        )

        with self.assertRaisesRegex(RuntimeError, "provider failed"):
            use_case.execute("https://youtube.com/playlist?list=failed")

        self.assertEqual(playlist_repository.get_all(), [])
        self.assertEqual(queue_stream_repository.saved, [])

    def test_update_changes_playlist_and_saves(self):
        existing = Playlist(name="Before", id="playlist-1")
        self.repository.playlists[existing.id] = existing
        use_case = UpdatePlaylistUseCase(self.repository)

        result = use_case.execute(
            "playlist-1",
            name="After",
            description="Updated",
            play_watched_streams=False,
            allow_duplicates=False,
            favorite=True,
            sort_order=4,
        )

        self.assertIs(result, existing)
        self.assertEqual(existing.name, "After")
        self.assertEqual(existing.description, "Updated")
        self.assertFalse(existing.playWatchedStreams)
        self.assertFalse(existing.allowDuplicates)
        self.assertTrue(existing.favorite)
        self.assertEqual(existing.sortOrder, 4)

    def test_update_missing_playlist_raises_domain_error(self):
        use_case = UpdatePlaylistUseCase(self.repository)

        with self.assertRaisesRegex(PlaylistNotFoundError, "playlist-missing"):
            use_case.execute("playlist-missing", name="After")

    def test_delete_existing_playlist_delegates_to_repository(self):
        playlist = Playlist(name="To delete", id="playlist-1")
        self.repository.playlists[playlist.id] = playlist
        use_case = DeletePlaylistUseCase(self.repository)

        use_case.execute("playlist-1")

        self.assertNotIn("playlist-1", self.repository.playlists)

    def test_delete_missing_playlist_raises_domain_error(self):
        use_case = DeletePlaylistUseCase(self.repository)

        with self.assertRaisesRegex(PlaylistNotFoundError, "playlist-missing"):
            use_case.execute("playlist-missing")

    def test_add_stream_to_playlist_appends_and_saves(self):
        playlist = Playlist(name="Favorites", streamIds=[], id="playlist-1")
        self.repository.playlists[playlist.id] = playlist
        use_case = AddStreamToPlaylistUseCase(self.repository)

        result = use_case.execute("playlist-1", "qs-1")

        self.assertIs(result, playlist)
        self.assertEqual(playlist.streamIds, ["qs-1"])

    def test_add_duplicate_stream_raises_domain_error(self):
        playlist = Playlist(name="Favorites", streamIds=["qs-1"], id="playlist-1")
        self.repository.playlists[playlist.id] = playlist
        use_case = AddStreamToPlaylistUseCase(self.repository)

        with self.assertRaisesRegex(DuplicateStreamError, "already in playlist"):
            use_case.execute("playlist-1", "qs-1")

    def test_add_stream_to_missing_playlist_raises_domain_error(self):
        use_case = AddStreamToPlaylistUseCase(self.repository)

        with self.assertRaisesRegex(PlaylistNotFoundError, "playlist-missing"):
            use_case.execute("playlist-missing", "qs-1")


class YoutubeProviderTests(unittest.TestCase):
    def test_fetch_playlist_normalizes_flat_entries_without_download(self):
        class FakeYoutubeDL:
            def __init__(self, options):
                self.options = options
                self.options_seen = options

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def extract_info(self, uri, download=False):
                self.uri = uri
                self.download = download
                return {
                    "title": "Playlist title",
                    "entries": [
                        {"id": "video-1", "title": "Video", "thumbnail": "https://thumbs.example/1.jpg"},
                        None,
                        {"title": "Missing ID"},
                    ],
                }

        with patch("infrastructure.providers.youtube_provider.yt_dlp.YoutubeDL", FakeYoutubeDL):
            playlist = YoutubeProvider().fetch_playlist("https://youtube.com/playlist?list=test")

        self.assertEqual(playlist["title"], "Playlist title")
        self.assertEqual(playlist["entries"], [
            {"id": "video-1", "title": "Video", "thumbnail": "https://thumbs.example/1.jpg"}
        ])


class YoutubePlaylistProviderStub:
    def __init__(self, playlist_metadata):
        self.playlist_metadata = playlist_metadata
        self.requested_url = None

    def fetch_playlist(self, uri):
        self.requested_url = uri
        return self.playlist_metadata


class CompositionRootTests(unittest.TestCase):
    def test_injected_ports_and_provider_reach_playlist_import_use_case(self):
        playlist_repository = PlaylistRepositoryStub()
        queue_stream_repository = QueueStreamRepositoryStub()
        stream_source_repository = StreamSourceRepositoryStub()
        provider = YoutubePlaylistProviderStub({
            "title": "Composed playlist",
            "entries": [{"id": "video-1", "title": "Video"}],
        })
        composition_root = CompositionRoot(
            playlist_repository=playlist_repository,
            queue_stream_repository=queue_stream_repository,
            stream_source_repository=stream_source_repository,
            external_stream_provider=provider,
        )

        playlist = composition_root.create_playlist_from_youtube.execute("https://example.com/playlist")

        self.assertIs(composition_root.playlist_repository, playlist_repository)
        self.assertIs(composition_root.queue_stream_repository, queue_stream_repository)
        self.assertIs(composition_root.stream_source_repository, stream_source_repository)
        self.assertIs(composition_root.external_stream_provider, provider)
        self.assertEqual(playlist.name, "Composed playlist")
        self.assertEqual(len(playlist.streamIds), 1)


class BaseServiceRepositoryAdapterTests(unittest.TestCase):
    def test_youtube_playlist_import_links_streams_saved_by_json_repositories(self):
        provider = YoutubePlaylistProviderStub({
            "title": "Persisted playlist",
            "entries": [
                {"id": "video-one", "title": "One"},
                {"id": "video-two", "title": "Two"},
            ],
        })

        with tempfile.TemporaryDirectory(dir="tests") as storage_path:
            with patch("infrastructure.repositories.base_service_playlist_repository.Settings") as playlist_settings, \
                 patch("infrastructure.repositories.base_service_queue_stream_repository.Settings") as stream_settings:
                for settings in (playlist_settings, stream_settings):
                    settings.return_value.localStoragePath = storage_path
                    settings.return_value.debug = False
                playlist_repository = BaseServicePlaylistRepository()
                queue_stream_repository = BaseServiceQueueStreamRepository()

            use_case = CreatePlaylistFromYoutubeUseCase(
                playlist_repository,
                queue_stream_repository,
                provider,
            )
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                playlist = use_case.execute("https://youtube.com/playlist?list=integration")
                stored_playlist = playlist_repository.get_by_id(playlist.id)
                stored_streams = [
                    queue_stream_repository.get_by_id(stream_id)
                    for stream_id in stored_playlist.streamIds
                ]

        self.assertIsNotNone(playlist.id)
        self.assertEqual(len(stored_streams), 2)
        self.assertEqual([stream.remoteId for stream in stored_streams], ["video-one", "video-two"])

    def test_entity_repositories_support_create_read_update_and_soft_delete(self):
        repository_specs = [
            (
                "infrastructure.repositories.base_service_playlist_repository.Settings",
                BaseServicePlaylistRepository,
                Playlist(name="Playlist"),
                "Playlist",
            ),
            (
                "infrastructure.repositories.base_service_queue_stream_repository.Settings",
                BaseServiceQueueStreamRepository,
                QueueStream(name="Stream", uri="https://example.com/stream"),
                "Stream",
            ),
            (
                "infrastructure.repositories.base_service_stream_source_repository.Settings",
                BaseServiceStreamSourceRepository,
                StreamSource(name="Source", uri="https://example.com/source"),
                "Source",
            ),
        ]

        with tempfile.TemporaryDirectory(dir="tests") as storage_path:
            for settings_path, repository_type, entity, initial_name in repository_specs:
                with self.subTest(entity=type(entity).__name__):
                    with patch(settings_path) as settings_class:
                        settings_class.return_value.localStoragePath = storage_path
                        settings_class.return_value.debug = False
                        repository = repository_type()

                    repository.save(entity)
                    self.assertTrue(entity.id)
                    self.assertEqual(repository.get_by_id(entity.id).name, initial_name)

                    entity.name = "Updated"
                    repository.save(entity)
                    self.assertEqual(repository.get_by_id(entity.id).name, "Updated")
                    all_entities = repository.get_all()
                    self.assertEqual(len(all_entities), 1)
                    self.assertEqual(all_entities[0].id, entity.id)
                    self.assertEqual(all_entities[0].name, "Updated")

                    repository.delete(entity.id)
                    self.assertIsNone(repository.get_by_id(entity.id))
                    self.assertEqual(repository.get_all(), [])


class ToggleQueueStreamWatchedUseCaseTests(unittest.TestCase):
    def setUp(self):
        self.repository = QueueStreamRepositoryStub()
        self.queue_stream = QueueStream(name="Video", id="qs-1")
        self.repository.queue_streams[self.queue_stream.id] = self.queue_stream
        self.use_case = ToggleQueueStreamWatchedUseCase(self.repository)

    def test_toggle_sets_watched_timestamp_and_saves(self):
        result = self.use_case.execute("qs-1")

        self.assertIs(result, self.queue_stream)
        self.assertIsInstance(result.watched, datetime)
        self.assertIs(self.repository.saved[-1], result)

    def test_toggle_clears_existing_watched_timestamp(self):
        self.queue_stream.watched = datetime(2026, 1, 1)

        result = self.use_case.execute("qs-1")

        self.assertIsNone(result.watched)

    def test_toggle_missing_queue_stream_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "qs-missing"):
            self.use_case.execute("qs-missing")


if __name__ == "__main__":
    unittest.main()
