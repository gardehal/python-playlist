from LocalJsonRepository import LocalJsonRepository
from model.Playlist import *
from myutil.Util import *
from typing import List
from model.QueueVideo import QueueVideo

T = Playlist

class PlaylistService():
    typeT = Playlist
    debug: bool = False
    storagePath: str = "Playlist"
    repository: LocalJsonRepository = None

    def __init__(self,
                 debug: bool = False,
                 storagePath: str = "Playlist"):
        self.debug: bool = debug
        self.storagePath: str = storagePath
        self.repository: str = LocalJsonRepository(self.typeT, self.debug, self.storagePath)

        mkdir(storagePath)

    def add(self, playlist: T) -> bool:
        """
        Add a new playlist.

        Args:
            playlist (Playlist): playlist to add

        Returns:
            bool: success = True
        """

        return self.repository.add(playlist)

    def get(self, id: str) -> T:
        """
        Get playlist by ID.

        Args:
            id (str): id of playlist to get

        Returns:
            Playlist: playlist if any, else None
        """

        return self.repository.get(id)

    def getAll(self) -> List[T]:
        """
        Get all playlists.

        Returns:
            List[Playlist]: playlists if any, else empty list
        """

        return self.repository.getAll()

    def update(self, playlist: T) -> bool:
        """
        Update Playlist.

        Args:
            playlist (Playlist): playlist to update

        Returns:
            bool: success = True
        """

        return self.repository.update(playlist)

    def remove(self, id: str) -> bool:
        """
        Remove playlist.

        Args:
            id (str): id of playlist to remove

        Returns:
            bool: success = True
        """

        return self.repository.remove(id)

    def addOrUpdate(self, playlist: T) -> bool:
        return False

    def play(self, playlistId: str, startIndex: int = 0, shuffle: bool = False) -> bool:
        """
        Start playing streams from this playlist.

        Args:
            playlistId (str): ID of playlist to play from
            startIndex (int): index to start playing from
            shuffle (bool): should videos be shuffled

        Returns:
            bool: success = True
        """

        return None

    def addStreams(self, playlistId: str, streams: List[QueueVideo]) -> int:


        _playlist = self.repository.get(playlistId)
        if(_playlist == None):
            return 0

        _addedIds = 0
        for stream in streams:
            if(stream.id == None):
                continue
            
            _playlist.streamIds.append(stream.id)
            _addedIds += 1

        _updateResult = self.repository.update(_playlist)
        if(_updateResult):
            return _addedIds
        else:
            return 0

    def removeStream(self, playlistId: str, index: int) -> bool:
        return None

    def removeSteamById(self, playlistId: str, streamId: int) -> bool:
        return None

    def moveStream(self, playlistId: str, streamId: str, toIndex: int) -> bool:
        return None