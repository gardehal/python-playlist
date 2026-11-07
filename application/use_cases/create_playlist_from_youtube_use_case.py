from typing import Optional
from grdUtil.InputUtil import sanitize
from ports.playlist_repository import PlaylistRepository
from ports.queue_stream_repository import QueueStreamRepository
from ports.external_stream_provider import ExternalStreamProvider
from model.Playlist import Playlist
from model.QueueStream import QueueStream

class CreatePlaylistFromYoutubeUseCase:
    """
    Use Case to create a new Playlist from a YouTube URL.
    """

    def __init__(self, 
                 playlist_repository: PlaylistRepository, 
                 queue_stream_repository: QueueStreamRepository,
                 external_stream_provider: ExternalStreamProvider) -> None:
        self._playlist_repository = playlist_repository
        self._queue_stream_repository = queue_stream_repository
        self._external_stream_provider = external_stream_provider

    def execute(self, url: str, name: Optional[str] = None, 
                description: Optional[str] = None, 
                play_watched_streams: bool = False, 
                allow_duplicates: bool = False, 
                favorite: bool = False, 
                sort_order: int = 0) -> Playlist:
        """
        Fetches playlist metadata through the provider and persists its QueueStreams.

        Returns:
            Playlist: The newly created playlist object.
        """
        playlist_metadata = self._external_stream_provider.fetch_playlist(url)
        new_playlist = Playlist(
            name=name or playlist_metadata.get("title") or "New YouTube Playlist",
            description=description or f"Playlist created from YouTube playlist: {url}",
            playWatchedStreams=play_watched_streams,
            allowDuplicates=allow_duplicates,
            favorite=favorite,
            sortOrder=sort_order,
            lastWatchedIndex=0,
            streamSourceIds=[],
            streamIds=[]
        )
        
        for entry in playlist_metadata.get("entries") or []:
            video_id = entry.get("id")
            if not video_id:
                continue

            queue_stream = QueueStream(
                name=sanitize(entry.get("title") or "No title"),
                uri=f"https://www.youtube.com/watch?v={video_id}",
                isWeb=True,
                remoteId=video_id,
                thumbnailUrl=entry.get("thumbnail"),
            )
            self._queue_stream_repository.save(queue_stream)
            if queue_stream.id:
                new_playlist.streamIds.append(queue_stream.id)

        self._playlist_repository.save(new_playlist)
        return new_playlist
