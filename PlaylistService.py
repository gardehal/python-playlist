import random
import subprocess
from LocalJsonRepository import LocalJsonRepository
from model.Playlist import *
from myutil.Util import *
from typing import List
from datetime import datetime
from model.QueueStream import QueueStream
from dotenv import load_dotenv

load_dotenv()
LOG_WATCHED = os.environ.get("LOG_WATCHED")
DOWNLOAD_WEB_STREAMS = os.environ.get("DOWNLOAD_WEB_STREAMS")
REMOVE_WATCHED_ON_FETCH = os.environ.get("REMOVE_WATCHED_ON_FETCH")
PLAYED_ALWAYS_WATCHED = os.environ.get("PLAYED_ALWAYS_WATCHED")
BROWSER_BIN = os.environ.get("BROWSER_BIN")
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")

T = Playlist

class PlaylistService():
    typeT = Playlist
    debug: bool = False
    storagePath: str = None
    playlistRepository: LocalJsonRepository = None
    QueueStreamRepository: LocalJsonRepository = None

    def __init__(self,
                 debug: bool = False,
                 storagePath: str = "."):
        self.debug: bool = debug
        self.storagePath: str = storagePath
        self.playlistRepository: str = LocalJsonRepository(self.typeT, self.debug, os.path.join(storagePath, "Playlist"))
        self.QueueStreamRepository: str = LocalJsonRepository(QueueStream, self.debug, os.path.join(storagePath, "QueueStream"))

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
            bool: finished = True
        """

        _playlist = self.playlistRepository.get(playlistId)
        if(_playlist == None):
            return False

        _streams = []
        _rawStreams = []
        for id in _playlist.streamIds:
            _stream = self.QueueStreamRepository.get(id)
            if(_stream == None):
                if(self.debug): printS("Stream ", id, " in playlist ", _playlist.name, " was not found. Consider removing it from the playlist and adding it again.", color=colors["WARNING"])
                continue
            _rawStreams.append(_stream)

        if(shuffle):
            _streams = random.shuffle(_rawStreams)
        else:
            _streams = _rawStreams[startIndex:]

        printS("Playing playlist ", _playlist.name, ".")
        printS("Starting at video ", (startIndex + 1), ", shuffle is ", ("on" if shuffle else "off"), ", repeat playlist is ", ("on" if repeatPlaylist else "off"), ", played videos set to watched is ", ("on" if PLAYED_ALWAYS_WATCHED else "off"), ".")

        try:
            for i, _stream in enumerate(_streams):
                subprocessStream = None
                if(_stream.isWeb):
                    subprocessStream = subprocess.Popen(f"call start {_stream.uri}", stdout=subprocess.PIPE, shell=True) # PID set by this is not PID of browser, just subprocess which opens browser
                    
                    # https://stackoverflow.com/questions/7989922/opening-a-process-with-popen-and-getting-the-pid
                    # subprocessStream = subprocess.Popen([BROWSER_BIN, f"{_stream.uri}"], stdout=subprocess.PIPE, shell=False) # PID set by this SHOULD be browser, but is not
                else:
                    # TODO
                    printS("Non-web streams currently not supported, skipping video ", _stream.name, color = colors["ERROR"])
                    continue

                streamOpensText = " (opening in your browser)" if _stream.isWeb else ""
                if(i < (len(_streams) - 1)):
                    input(f"Now playing {_stream.name}" + streamOpensText + ", press enter to play next...")
                else:
                    input(f"Now playing last stream in playlist, {_stream.name}" + streamOpensText + ", press enter to finish.")
                
                # subprocessStream.terminate() # TODO Doesn't seem to work with browser, at least not new tabs
                
                now = datetime.now()
                if(LOG_WATCHED and len(WATCHED_LOG_FILEPATH) > 0):
                    logLine = f"{str(now)} - Playlist \"{_playlist.name}\" (ID: {_playlist.id}), watched video \"{_stream.name}\" (ID: {_stream.id})\n" 
                    with open(WATCHED_LOG_FILEPATH, "a") as file:
                        file.write(logLine)
                        
                if(PLAYED_ALWAYS_WATCHED):
                    _stream.watched = now
        except:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            #printS("handleing of streams encountered an issue.", color=colors["WARNING"])

        printS("Playlist ", _playlist.name, " finished.")

        if(repeatPlaylist):
            self.playCmd(playlistId, startIndex, shuffle, repeatPlaylist)

        return True

    def addStreams(self, playlistId: str, streams: List[QueueStream]) -> int:
        """
        Add streams to playlist.

        Args:
            playlistId (str): ID of playlist to add to
            streams (List[QueueStream]): streams to add

        Returns:
            int: number of streams added
        """

        _playlist = self.playlistRepository.get(playlistId)
        if(_playlist == None):
            return 0

        _added = 0
        for stream in streams:
            if(stream.id == None):
                continue
            
            _playlist.streamIds.append(stream.id)
            _added += 1

        _playlist.lastUpdated = datetime.now()
        _updateResult = self.playlistRepository.update(_playlist)
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

        _playlist = self.playlistRepository.get(playlistId)
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
        _updateResult = self.playlistRepository.update(_playlist)
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

        _playlist = self.playlistRepository.get(playlistId)
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
        return self.playlistRepository.update(_playlist)