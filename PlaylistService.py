from LocalJsonRepository import LocalJsonRepository
from model.Playlist import *
from myutil.Util import *
from typing import List
from datetime import datetime
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
        """
        Add playlist if none exists, else update existing.

        Args:
            playlist (T): playlist to add or update

        Returns:
            bool: success = True
        """

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

        return False

    def addStreams(self, playlistId: str, streams: List[QueueVideo]) -> int:
        """
        Add streams to playlist.

        Args:
            playlistId (str): ID of playlist to add to
            streams (List[QueueVideo]): streams to add

        Returns:
            int: number of streams added
        """

        _playlist = self.repository.get(playlistId)
        if(_playlist == None):
            return 0

        _added = 0
        for stream in streams:
            if(stream.id == None):
                continue
            
            _playlist.streamIds.append(stream.id)
            _added += 1

        _playlist.lastUpdated = datetime.now()
        _updateResult = self.repository.update(_playlist)
        if(_updateResult):
            return _added
        else:
            return 0

    def removeStreams(self, playlistId: str, indices: List[int]) -> int:
        """
        Remove streams to playlist.

        Args:
            playlistId (str): ID of playlist to remove from
            indices (List[int]): indices to remove

        Returns:
            int: number of streams removed
        """

        _playlist = self.repository.get(playlistId)
        if(_playlist == None):
            return 0

        _listLength = len(_playlist.streamIds)
        indices.sort(reverse=True)
        _removed = 0
        for index in indices:
            if(index < 0 or index >= _listLength):
                printS("Index ", index, " was out or range.", color=colors["WARNING"])
                continue
            
            _playlist.streamIds.pop(index)
            _removed += 1

        _playlist.lastUpdated = datetime.now()
        _updateResult = self.repository.update(_playlist)
        if(_updateResult):
            return _removed
        else:
            return 0

    def moveStream(self, playlistId: str, fromIndex: int, toIndex: int) -> bool:
        """
        Move streams in playlist.

        Args:
            playlistId (str): ID of playlist to move in
            fromIndex (int): index move
            toIndex (int): index to move to

        Returns:
            bool: success = True
        """

        _playlist = self.repository.get(playlistId)
        if(_playlist == None):
            return 0

        _listLength = len(_playlist.streamIds)
        if(fromIndex == toIndex):
            if(self.debug): printS("Index from and to were the same. No update needed.", color=colors["WARNING"])
            return True
        if(fromIndex < 0 or fromIndex >= _listLength):
            printS("Index to move from (", fromIndex, ") was out or range.", color=colors["WARNING"])
            return False
        if(toIndex < 0 or toIndex >= _listLength):
            printS("Index to move to (", toIndex, ") was out or range.", color=colors["WARNING"])
            return False

        ## TODO check before/after and how stuff moves?
        entry = _playlist.streamIds[fromIndex]
        _playlist.streamIds.pop(fromIndex)
        _playlist.streamIds.insert(toIndex, entry)

        _playlist.lastUpdated = datetime.now()
        return self.repository.update(_playlist)