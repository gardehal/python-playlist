import os
import random
import subprocess
from datetime import datetime
from typing import List
import uuid

from dotenv import load_dotenv
from myutil.LocalJsonRepository import LocalJsonRepository
from myutil.Util import *

from QueueStreamService import QueueStreamService
from StreamSourceService import StreamSourceService
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")
LOG_WATCHED = eval(os.environ.get("LOG_WATCHED"))
DOWNLOAD_WEB_STREAMS = eval(os.environ.get("DOWNLOAD_WEB_STREAMS"))
REMOVE_WATCHED_ON_FETCH = eval(os.environ.get("REMOVE_WATCHED_ON_FETCH"))
PLAYED_ALWAYS_WATCHED = eval(os.environ.get("PLAYED_ALWAYS_WATCHED"))
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")
BROWSER_BIN = os.environ.get("BROWSER_BIN")

T = Playlist

class PlaylistService():
    debug: bool = DEBUG
    storagePath: str = LOCAL_STORAGE_PATH
    playlistRepository: LocalJsonRepository = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    quitInputs: List[str] = None
    skipInputs: List[str] = None
    addToInputs: List[str] = None

    def __init__(self, quitInputs: List[str] = ["quit"], skipInputs: List[str] = ["skip"], addToInputs: List[str] = ["addto"]):
        self.playlistRepository: LocalJsonRepository = LocalJsonRepository(T, self.debug, os.path.join(self.storagePath, "Playlist"))
        self.queueStreamService: QueueStreamService = QueueStreamService()
        self.streamSourceService: StreamSourceService = StreamSourceService()
        self.quitInputs: List[str] = quitInputs
        self.skipInputs: List[str] = skipInputs
        self.addToInputs: List[str] = addToInputs

    def add(self, playlist: T) -> T:
        """
        Add a new playlist.

        Args:
            playlist (Playlist): playlist to add

        Returns:
            Playlist | None: returns Playlist if success, else None
        """

        _entity = playlist
        _entity.id = str(uuid.uuid4())
        _entity.updated = datetime.now()
        _entity.added = datetime.now()
        _result = self.playlistRepository.add(_entity)
        if(_result):
            return _entity
        else:
            return None

    def get(self, id: str, includeSoftDeleted: bool = False) -> T:
        """
        Get Playlist by ID.

        Args:
            id (str): ID of Playlist to get
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            Playlist: Playlist if any, else None
        """

        _entity = self.playlistRepository.get(id)
        
        if(_entity.deleted != None and not includeSoftDeleted):
            printS("Playlist with ID ", _entity.id, " was soft deleted.", color=colors["WARNING"], doPrint = DEBUG)
            return None
        else:
            return _entity

    def getAll(self, includeSoftDeleted: bool = False) -> List[T]:
        """
        Get all Playlists.

        Args:
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[Playlist]: list of Playlists
        """

        _entities = self.playlistRepository.getAll()
        _result = []
        
        for _entity in _entities:
            if(_entity.deleted != None and not includeSoftDeleted):
                printS("Playlist with ID ", _entity.id, " was soft deleted.", color=colors["WARNING"], doPrint = DEBUG)
            else:
                _result.append(_entity)
            
        return _result
        
    def getAllIds(self) -> List[str]:
        """
        Get all IDs of playlists.

        Returns:
            List[str]: playlists IDs if any, else empty list
        """
        
        _all = self.getAll()
        return [_.id for _ in _all]

    def update(self, playlist: T) -> T:
        """
        Update Playlist.

        Args:
            playlist (Playlist): playlist to update

        Returns:
            Playlist | None: returns Playlist if success, else None
        """

        _entity = playlist
        _entity.updated = datetime.now()
        _result = self.playlistRepository.update(_entity)
        if(_result):
            return _entity
        else:
            return None

    def delete(self, id: str) -> T:
        """
        (Soft) Delete a Playlist.

        Args:
            id (str): ID of Playlist to delete

        Returns:
            Playlist | None: returns Playlist if success, else None
        """

        _entity = self.get(id)
        if(_entity == None):
            return None

        _entity.deleted = datetime.now()
        _result = self.update(_entity)
        if(_result):
            return _entity
        else:
            return None
        
    def remove(self, id: str) -> T:
        """
        Permanently remove a Playlist.

        Args:
            id (str): ID of Playlist to remove

        Returns:
            Playlist | None: returns Playlist if success, else None
        """

        _entity = self.get(id)
        if(_entity == None):
            return None
        
        _result = self.playlistRepository.remove(_entity.id)
        if(_result):
            return _entity
        else:
            return None

    def addOrUpdate(self, playlist: T) -> T:
        """
        Add playlist if none exists, else update existing.

        Args:
            playlist (T): playlist to add or update

        Returns:
            Playlist | None: returns Playlist if success, else None
        """

        if(self.get(playlist.id) == None):
            return self.add(playlist)

        return self.update(playlist)

    def playCmd(self, playlistId: str, startIndex: int = 0, shuffle: bool = False, repeatPlaylist: bool = False) -> bool:
        """
        Start playing streams from this playlist.

        Args:
            playlistId (str): ID of playlist to play from
            quitSymbols (List[str]): input from user which should end the playback. Defaults to ["quit"]
            startIndex (int): index to start playing from
            shuffle (bool): shuffle videos
            repeatPlaylist (bool): repeat playlist once it reaches the end

        Returns:
            bool: finished = True
        """

        _playlist = self.get(playlistId)
        if(_playlist == None):
            return False

        if(len(_playlist.streamIds) == 0):
            printS("No streams found in playlist \"", _playlist.name, "\". Ending playback.")
            return False

        _streams = []
        _rawStreams = self.getStreamsByPlaylistId(_playlist.id)

        if(len(_rawStreams) == 0):
            printS("Playlist \"", _playlist.name, "\" has ", len(_streams), " streams, but they could not be found in database (they may have been removed). Ending playback.")
            return False

        if(shuffle):
            _streams = random.shuffle(_rawStreams)
        else:
            _streams = _rawStreams[startIndex:]

        printS("Playing playlist ", _playlist.name, ".")
        printS("Starting at stream number: ", (startIndex + 1), ", shuffle is ", ("on" if shuffle else "off"), ", repeat playlist is ", ("on" if repeatPlaylist else "off"), ", played videos set to watched is ", ("on" if PLAYED_ALWAYS_WATCHED else "off"), ".")

        try:
            for i, _stream in enumerate(_streams):
                if(_stream.watched != None and not _playlist.playWatchedStreams):
                    _checkLogsMessage = " Check your logs (" + WATCHED_LOG_FILEPATH + ") for date/time watched." if LOG_WATCHED else " Logging is disabled and date/time watched is not available."
                    printS("Stream \"", _stream.name, "\" (ID: ", _stream.id, ") has been marked as watched.", _checkLogsMessage, color = colors["WARNING"])
                    continue

                subprocessStream = None
                if(_stream.isWeb):
                    subprocessStream = subprocess.Popen(f"call start {_stream.uri}", stdout=subprocess.PIPE, shell=True) # PID set by this is not PID of browser, just subprocess which opens browser
                    
                    # https://stackoverflow.com/questions/7989922/opening-a-process-with-popen-and-getting-the-pid
                    # subprocessStream = subprocess.Popen([BROWSER_BIN, f"{_stream.uri}"], stdout=subprocess.PIPE, shell=False) # PID set by this SHOULD be browser, but is not
                else:
                    # TODO
                    printS("Non-web streams currently not supported, skipping video ", _stream.name, color = colors["ERROR"])
                    continue

                printS(f"Now playing \"{_stream.name}\"" + ("..." if(i < (len(_streams) - 1)) else ". This is the last stream, press enter to finish."), color = colors["BOLD"])
                _input = input("\tPress enter to play next, \"skip\" to skip video, or \"quit\" to quit playback: ")
                if(len(self.quitInputs) > 0 and _input in self.quitInputs):
                    printS("Ending playback due to user input.", color = colors["OKGREEN"])
                    break
                elif(len(self.skipInputs) > 0 and _input in self.skipInputs):
                    printS("Skipping video, will not be marked as watched.", color = colors["OKGREEN"])
                    continue
                elif(len(self.addToInputs) > 0 and _input in self.addToInputs):
                    # TODO add
                    printS("Video added to x.", color = colors["OKGREEN"])
                
                # subprocessStream.terminate() # TODO Doesn't seem to work with browser, at least not new tabs
                
                now = datetime.now()
                if(LOG_WATCHED and len(WATCHED_LOG_FILEPATH) > 0):
                    logLine = f"{str(now)} - Playlist \"{_playlist.name}\" (ID: {_playlist.id}), watched video \"{_stream.name}\" (ID: {_stream.id})\n" 
                    with open(WATCHED_LOG_FILEPATH, "a") as file:
                        file.write(logLine)
                        
                if(PLAYED_ALWAYS_WATCHED):
                    _stream.watched = now
                    
                    _updateSuccess = self.queueStreamService.update(_stream)
                    if(not _updateSuccess):
                        printS("Stream \"", _stream.name, "\" could not be updated as watched.", color=colors["WARNING"])
        except:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            #printS("handleing of streams encountered an issue.", color=colors["WARNING"])

        printS("Playlist \"", _playlist.name, "\" finished.")

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

        _playlist = self.get(playlistId)
        if(_playlist == None):
            return 0

        _playlistStreamUris = []
        if(not _playlist.allowDuplicates):
            _playlistStreams = self.getStreamsByPlaylistId(_playlist.id)
            _playlistStreamUris = [_.uri for _ in _playlistStreams]
            
        _added = 0
        for stream in streams:            
            if(not _playlist.allowDuplicates and stream.uri in _playlistStreamUris):
                printS("Stream \"", stream.name, "\" already exists in playlist \"", _playlist.name, "\" and allow duplicates for this playlist is disabled.", color=colors["WARNING"])
                continue

            _addResult = self.queueStreamService.add(stream)            
            if(_addResult == None):
                printS("Stream \"", stream.name, "\" could not be added.", color=colors["FAIL"])
                continue

            _playlist.streamIds.append(stream.id)
            _added += 1

        _playlist.updated = datetime.now()
        _updateResult = self.update(_playlist)
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

        _playlist = self.get(playlistId)
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

        _playlist.updated = datetime.now()
        _updateResult = self.update(_playlist)
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

        _playlist = self.get(playlistId)
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

        _playlist.updated = datetime.now()
        return self.update(_playlist)

    def getStreamsByPlaylistId(self, playlistId: str) -> List[QueueStream]:
        """
        Get all QueueStreams in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to add to

        Returns:
            List[QueueStream]: QueueStreams if any, else empty list
        """

        _playlist = self.get(playlistId)
        if(_playlist == None):
            return 0

        _all = self.queueStreamService.getAll()
        _playlistStreams = []
        for _stream in _all:
            if(_stream.id in _playlist.streamIds):
                _playlistStreams.append(_stream)

        return _playlistStreams
    
    def getUnwatchedStreamsByPlaylistId(self, playlistId: str) -> List[QueueStream]:
        """
        Get unwatched QueueStreams in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to get from

        Returns:
            List[QueueStream]: QueueStreams if any, else empty list
        """

        _playlist = self.get(playlistId)
        if(_playlist == None):
            return 0

        _all = self.queueStreamService.getAll()
        _playlistStreams = []
        for _stream in _all:
            if(_stream.id in _playlist.streamIds and _stream.watched == None):
                _playlistStreams.append(_stream)

        return _playlistStreams    
    
    def getFetchedSourcesByPlaylistId(self, playlistId: str) -> List[StreamSource]:
        """
        Get StreamSources where fetch is enabled in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to get from

        Returns:
            List[StreamSource]: StreamSources if any, else empty list
        """

        _playlist = self.get(playlistId)
        if(_playlist == None):
            return 0

        _all = self.streamSourceService.getAll()
        _playlistSources = []
        for _source in _all:
            if(_source.id in _playlist.streamSourceIds and _source.enableFetch == True):
                _playlistSources.append(_source)

        return _playlistSources

    def createFromYouTubePlaylist(self, url: str) -> T:
        """
        Create a Playlist, using a YouTube playlist as the starting point. Videos will be added as streams in the playlist TODO? and source will be the playlist.

        Args:
            url (str): URI to YouTube playlist

        Returns:
            Playlist: Playlist if created, else None
        """
        
        _sanitizedTitle = ""
        _entity = Playlist(_sanitizedTitle, [], )
        self.add(_entity)
        
        return None
    
    def prune(self, playlistId: str) -> List[QueueStream]:
        """
        Removes watched streams from a Playlist if it does not allow replaying of already played streams (playWatchedStreams == False).

        Args:
            playlistId (str): ID of playlist to prune

        Returns:
            List[QueueStream]: QueueStreams removed
        """
        
        _removedStreams = []

        _playlist = self.get(playlistId)
        if(_playlist == None or _playlist.playWatchedStreams == True):
            return _removedStreams
        
        for _id in _playlist.streamIds:
            _stream = self.queueStreamService.get(_id)
            if(_stream.watched != None):
                _removedStreams.append(_stream)
                self.queueStreamService.remove(_id)
            
        for _stream in _removedStreams:
            _playlist.streamIds.remove(_stream.id)
            
        _updateResult = self.update(_playlist)
        if(_updateResult != None):
            return _removedStreams
        else:
            return []
        