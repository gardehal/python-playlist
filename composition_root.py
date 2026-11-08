from typing import Optional

from application.use_cases.add_stream_to_playlist_use_case import AddStreamToPlaylistUseCase
from application.use_cases.add_stream_source_to_playlist_use_case import AddStreamSourceToPlaylistUseCase
from application.use_cases.copy_queue_stream_to_playlists_use_case import CopyQueueStreamToPlaylistsUseCase
from application.use_cases.create_playlist_from_youtube_use_case import CreatePlaylistFromYoutubeUseCase
from application.use_cases.create_playlist_use_case import CreatePlaylistUseCase
from application.use_cases.create_queue_stream_use_case import CreateQueueStreamUseCase
from application.use_cases.create_stream_source_use_case import CreateStreamSourceUseCase
from application.use_cases.delete_playlist_use_case import DeletePlaylistUseCase
from application.use_cases.delete_queue_stream_use_case import DeleteQueueStreamUseCase
from application.use_cases.delete_stream_source_use_case import DeleteStreamSourceUseCase
from application.use_cases.download_playlist_use_case import DownloadPlaylistUseCase
from application.use_cases.fetch_playlist_use_case import FetchPlaylistUseCase
from application.use_cases.get_soft_deleted_entities_use_case import GetSoftDeletedEntitiesUseCase
from application.use_cases.get_all_playlists_use_case import GetAllPlaylistsUseCase
from application.use_cases.get_all_queue_streams_use_case import GetAllQueueStreamsUseCase
from application.use_cases.get_all_stream_sources_use_case import GetAllStreamSourcesUseCase
from application.use_cases.get_playlist_details_use_case import GetPlaylistDetailsUseCase
from application.use_cases.get_playlist_use_case import GetPlaylistUseCase
from application.use_cases.get_queue_stream_details_use_case import GetQueueStreamDetailsUseCase
from application.use_cases.get_queue_stream_playback_urls_use_case import GetQueueStreamPlaybackUrlsUseCase
from application.use_cases.get_stream_source_details_use_case import GetStreamSourceDetailsUseCase
from application.use_cases.prune_watched_queue_streams_use_case import PruneWatchedQueueStreamsUseCase
from application.use_cases.purge_soft_deleted_entities_use_case import PurgeSoftDeletedEntitiesUseCase
from application.use_cases.toggle_queue_stream_watched_use_case import ToggleQueueStreamWatchedUseCase
from application.use_cases.update_playlist_use_case import UpdatePlaylistUseCase
from application.use_cases.update_queue_stream_use_case import UpdateQueueStreamUseCase
from application.use_cases.update_stream_source_use_case import UpdateStreamSourceUseCase
from infrastructure.providers.youtube_provider import YoutubeProvider
from infrastructure.providers.legacy_download_service_adapter import LegacyDownloadServiceAdapter
from infrastructure.providers.legacy_fetch_service_adapter import LegacyFetchServiceAdapter
from infrastructure.repositories.base_service_playlist_repository import BaseServicePlaylistRepository
from infrastructure.repositories.base_service_queue_stream_repository import BaseServiceQueueStreamRepository
from infrastructure.repositories.base_service_stream_source_repository import BaseServiceStreamSourceRepository
from ports.external_stream_provider import ExternalStreamProvider
from ports.playlist_repository import PlaylistRepository
from ports.playlist_fetch_provider import PlaylistFetchProvider
from ports.queue_stream_repository import QueueStreamRepository
from ports.stream_source_repository import StreamSourceRepository
from ports.stream_download_provider import StreamDownloadProvider


class CompositionRoot:
    def __init__(
        self,
        playlist_repository: Optional[PlaylistRepository] = None,
        queue_stream_repository: Optional[QueueStreamRepository] = None,
        stream_source_repository: Optional[StreamSourceRepository] = None,
        external_stream_provider: Optional[ExternalStreamProvider] = None,
        playlist_fetch_provider: Optional[PlaylistFetchProvider] = None,
        stream_download_provider: Optional[StreamDownloadProvider] = None,
    ) -> None:
        self.playlist_repository = playlist_repository or BaseServicePlaylistRepository()
        self.queue_stream_repository = queue_stream_repository or BaseServiceQueueStreamRepository()
        self.stream_source_repository = stream_source_repository or BaseServiceStreamSourceRepository()
        self.external_stream_provider = external_stream_provider or YoutubeProvider()
        self.playlist_fetch_provider = playlist_fetch_provider or LegacyFetchServiceAdapter()
        self.stream_download_provider = stream_download_provider or LegacyDownloadServiceAdapter()

        self.add_stream_to_playlist = AddStreamToPlaylistUseCase(self.playlist_repository)
        self.add_stream_source_to_playlist = AddStreamSourceToPlaylistUseCase(self.playlist_repository)
        self.copy_queue_stream_to_playlists = CopyQueueStreamToPlaylistsUseCase(
            self.playlist_repository,
            self.queue_stream_repository,
        )
        self.create_playlist = CreatePlaylistUseCase(self.playlist_repository)
        self.create_playlist_from_youtube = CreatePlaylistFromYoutubeUseCase(
            self.playlist_repository,
            self.queue_stream_repository,
            self.external_stream_provider,
        )
        self.create_queue_stream = CreateQueueStreamUseCase(self.queue_stream_repository)
        self.create_stream_source = CreateStreamSourceUseCase(self.stream_source_repository)
        self.delete_playlist = DeletePlaylistUseCase(self.playlist_repository)
        self.delete_queue_stream = DeleteQueueStreamUseCase(self.queue_stream_repository)
        self.delete_stream_source = DeleteStreamSourceUseCase(self.stream_source_repository)
        self.download_playlist = DownloadPlaylistUseCase(
            self.playlist_repository,
            self.queue_stream_repository,
            self.stream_download_provider,
        )
        self.fetch_playlist = FetchPlaylistUseCase(
            self.playlist_repository,
            self.playlist_fetch_provider,
        )
        self.get_soft_deleted_entities = GetSoftDeletedEntitiesUseCase(
            self.playlist_repository,
            self.queue_stream_repository,
            self.stream_source_repository,
        )
        self.get_all_playlists = GetAllPlaylistsUseCase(self.playlist_repository)
        self.get_all_queue_streams = GetAllQueueStreamsUseCase(self.queue_stream_repository)
        self.get_all_stream_sources = GetAllStreamSourcesUseCase(self.stream_source_repository)
        self.get_playlist_details = GetPlaylistDetailsUseCase(
            self.playlist_repository,
            self.queue_stream_repository,
            self.stream_source_repository,
        )
        self.get_playlist = GetPlaylistUseCase(self.playlist_repository)
        self.get_queue_stream_details = GetQueueStreamDetailsUseCase(self.queue_stream_repository)
        self.get_queue_stream_playback_urls = GetQueueStreamPlaybackUrlsUseCase()
        self.get_stream_source_details = GetStreamSourceDetailsUseCase(self.stream_source_repository)
        self.prune_watched_queue_streams = PruneWatchedQueueStreamsUseCase(
            self.playlist_repository,
            self.queue_stream_repository,
        )
        self.purge_soft_deleted_entities = PurgeSoftDeletedEntitiesUseCase(
            self.playlist_repository,
            self.queue_stream_repository,
            self.stream_source_repository,
        )
        self.toggle_queue_stream_watched = ToggleQueueStreamWatchedUseCase(self.queue_stream_repository)
        self.update_playlist = UpdatePlaylistUseCase(self.playlist_repository)
        self.update_queue_stream = UpdateQueueStreamUseCase(self.queue_stream_repository)
        self.update_stream_source = UpdateStreamSourceUseCase(self.stream_source_repository)
