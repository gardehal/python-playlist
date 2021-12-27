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
    storagePath: str = None
    playlistRepository: LocalJsonRepository = None
    queueVideoRepository: LocalJsonRepository = None

    def __init__(self,
                 debug: bool = False,
                 storagePath: str = "."):
        self.debug: bool = debug
        self.storagePath: str = storagePath
        self.playlistRepository: str = LocalJsonRepository(self.typeT, self.debug, os.path.join(storagePath, "Playlist"))
        self.queueVideoRepository: str = LocalJsonRepository(QueueVideo, self.debug, os.path.join(storagePath, "QueueVideo"))

        mkdir(storagePath)

    def add(self, playlist: T) -> bool:
        """
        Add a new playlist.

        Args:
            playlist (Playlist): playlist to add

        Returns:
            bool: success = True
        """

        return self.playlistRepository.add(playlist)

    def get(self, id: str) -> T:
        """
        Get playlist by ID.

        Args:
            id (str): id of playlist to get

        Returns:
            Playlist: playlist if any, else None
        """

        return self.playlistRepository.get(id)

    def getAll(self) -> List[T]:
        """
        Get all playlists.

        Returns:
            List[Playlist]: playlists if any, else empty list
        """

        return self.playlistRepository.getAll()

    def update(self, playlist: T) -> bool:
        """
        Update Playlist.

        Args:
            playlist (Playlist): playlist to update

        Returns:
            bool: success = True
        """

        return self.playlistRepository.update(playlist)

    def remove(self, id: str) -> bool:
        """
        Remove playlist.

        Args:
            id (str): id of playlist to remove

        Returns:
            bool: success = True
        """

        return self.playlistRepository.remove(id)

    def addOrUpdate(self, playlist: T) -> bool:
        """
        Add playlist if none exists, else update existing.

        Args:
            playlist (T): playlist to add or update

        Returns:
            bool: success = True
        """

        if(self.add(playlist)):
            return True

        return self.update(playlist)

    def playCmd(self, playlistId: str, startIndex: int = 0, shuffle: bool = False, repeatPlaylist: bool = False) -> bool:
        """
        Start playing streams from this playlist.

        Args:
            playlistId (str): ID of playlist to play from
            startIndex (int): index to start playing from
            shuffle (bool): shuffle videos
            repeatPlaylist (bool): repeat playlist once it reaches the end

        Returns:
            bool: success = True
        """

        _playlist = self.playlistRepository.get(playlistId)
        if(_playlist == None):
            return False

        _streams = []
        for id in _playlist.streamIds:
            _stream = self.queueVideoRepository.get(id)
            if(_stream == None):
                if(self.debug): printS("Stream ", id, " in playlist ", _playlist.name, " was not found. Consider removing it from the playlist and adding it again.", color=colors["WARNING"])
                continue
            _streams.append(_stream)

        _streams = _streams[startIndex:]

        # make list of qv to play
        # open new cmdwindow
        # open browser to link of video if web source, else is local file, play though VLC (use default player if can be grabbed by python)
        # display something like "video is playing, press any key to play next" in new window
        # optional: get length of video, when video is done, open next video automatically (what id user pauses video)

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