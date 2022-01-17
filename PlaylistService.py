import os
from datetime import datetime
from typing import List
import uuid

from dotenv import load_dotenv
from myutil.LocalJsonRepository import LocalJsonRepository
from myutil.Util import *
import pytube

from QueueStreamService import QueueStreamService
from StreamSourceService import StreamSourceService
from Utility import Utility
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

affirmative = ["yes", "y", "1"]
negative = ["no", "n", "0"]

class PlaylistService():
    debug: bool = DEBUG
    storagePath: str = LOCAL_STORAGE_PATH
    playlistRepository: LocalJsonRepository = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    utility: Utility = None

    def __init__(self):
        self.playlistRepository: LocalJsonRepository = LocalJsonRepository(T, self.debug, os.path.join(self.storagePath, "Playlist"))
        self.queueStreamService: QueueStreamService = QueueStreamService()
        self.streamSourceService: StreamSourceService = StreamSourceService()
        self.utility: Utility = Utility()

    def add(self, playlist: T) -> T:
        """
        Add a new playlist.

        Args:
            playlist (Playlist): playlist to add

        Returns:
            Playlist | None: returns Playlist if success, else None
        """

        _entity = playlist
        _entity.updated = datetime.now()
        _entity.deleted = None
        _entity.added = datetime.now()
        _entity.id = str(uuid.uuid4())
        
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
        
        if(_entity != None and _entity.deleted != None and not includeSoftDeleted):
            printS("Playlist with ID ", _entity.id, " was soft deleted.", color = colors["WARNING"], doPrint = DEBUG)
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

    def deleteStreams(self, playlistId: str, streamIds: List[str]) -> List[QueueStream]:
        """
        Delete streams from Playlist.

        Args:
            playlistId (str): ID of Playlist to remove from
            streamIds (List[str]): IDs of QueueStreams to remove

        Returns:
            List[QueueStream]: QueueStream deleted
        """

        _removed = []
        _playlist = self.get(playlistId)
        if(_playlist == None):
            return _removed

        for id in streamIds:
            _stream = self.queueStreamService.get(id)
            if(_stream == None):
                continue
            
            _removeResult = self.queueStreamService.delete(id)
            if(_removeResult != None):
                _playlist.streamIds.remove(_stream.id)
                _removed.append(_stream)

        _playlist.updated = datetime.now()
        _updateResult = self.update(_playlist)
        if(_updateResult):
            return _removed
        else:
            return []

    def moveStream(self, playlistId: str, fromIndex: int, toIndex: int) -> bool:
        """
        Move streams internally in Playlist, by index.

        Args:
            playlistId (str): ID of Playlist to move in
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

        _playlistStreams = []
        for id in _playlist.streamIds:
            _stream = self.queueStreamService.get(id)
            if(_stream == None):
                printS("A QueueStream with ID: ", id, " was listed in Playlist \"", _playlist.name, "\", but was not found in the database. Consider removing it by running the purge command.", color = colors["WARNING"])
                continue
            
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

        _playlistStreams = []
        for id in _playlist.streamIds:
            _stream = self.queueStreamService.get(id)
            if(_stream == None):
                printS("A QueueStream with ID: ", id, " was listed in Playlist \"", _playlist.name, "\", but was not found in the database. Consider removing it by running the purge command.", color = colors["WARNING"])
                continue
            
            if(_stream.watched == None):
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

        _playlistSources = []
        for id in _playlist.streamSourceIds:
            _source = self.streamSourceService.get(id)
            if(_source == None):
                printS("A StreamSource with ID: ", id, " was listed in Playlist \"", _playlist.name, "\", but was not found in the database. Consider removing it by running the purge command.", color = colors["WARNING"])
                continue
            
            if(_source.enableFetch == True):
                _playlistSources.append(_source)

        return _playlistSources

    def addYouTubePlaylist(self, playlist: Playlist, url: str) -> T:
        """
        Create a Playlist, using a YouTube playlist as the starting point. Videos will be added as streams in the playlist TODO? and source will be the playlist.

        Args:
            playlist (Playlist): Playlist to save to
            url (str): URI to YouTube playlist

        Returns:
            Playlist: Playlist if created, else None
        """
        
        if(playlist == None):
            printS("Playlist was None.", color = colors["FAIL"])
            return None
        
        if(not validators.url(url)):
            printS("URL \"", url, "\" was not an accepted, absolute URL.", color = colors["FAIL"])
            return None
        
        ytPlaylist = pytube.Playlist(url)
        try:
            # For some reasons the property call just fails for invalid playlist, instead of being None. Except = fail.
            ytPlaylist.title == None
        except:
            printS("YouTube playlist given by URL \"", url, "\" was not found. It could be set to private or deleted.", color = colors["FAIL"])
            return None
        
        if(playlist.name == None):
            playlist.name = sanitize(ytPlaylist.title)
        if(playlist.description == None):
            playlist.description = f"Playlist created from YouTube playlist: {url}"
        
        _streamsToAdd = []
        for videoUrl in ytPlaylist.video_urls:
            _video = pytube.YouTube(videoUrl)
            _stream = QueueStream(name = sanitize(_video.title), uri = _video.watch_url)
            _streamsToAdd.append(_stream)
        
        _addPlaylistResult = self.add(playlist)
        if(_addPlaylistResult != None):
            _addStreamsResult = self.addStreams(_addPlaylistResult.id, _streamsToAdd)
            if(_addStreamsResult > 0):
                return _addPlaylistResult
            
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
        
    def purge(self, removeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> dict[List[QueueStream], List[StreamSource]]:
        """
        Purges the dangling IDs, StreamSources, and QueueStreams from Playlists.

        Args:
            removeSoftDeleted (bool): should soft-deleted entities be deleted
            permanentlyDelete (bool): should entities be permanently deleted
            
        Returns:
            dict[List[QueueStream], List[StreamSource]]: dict with two lists, one for StreamSources removed, one for QueueStreams removed
        """
        
        _deletedData = {"QueueStream": [], "StreamSource": [], "DanglingQueueStreamId": [], "DanglingStreamSourceId": []}
        _playlists = self.getAll(removeSoftDeleted)
        _streamsIds = self.queueStreamService.getAllIds()
        _sourcesIds = self.streamSourceService.getAllIds()
        
        _playlistStreams = []
        _playlistSources = []
        _updatedPlaylists = []
        for _playlist in _playlists:
            _playlistStreams.extend(_playlist.streamIds)
            _playlistSources.extend(_playlist.streamSourceIds)
        
        for _id in _streamsIds:
            if(not _id in _playlistStreams):
                _entity = self.queueStreamService.get(_id, removeSoftDeleted)
                _deletedData["QueueStream"].append(_entity)
        for _id in _sourcesIds:
            if(not _id in _playlistSources):
                _entity = self.streamSourceService.get(_id, removeSoftDeleted)
                _deletedData["StreamSource"].append(_entity)
                
        for _playlist in _playlists:
            for _id in _playlist.streamIds:
                _stream = self.queueStreamService.get(_id, removeSoftDeleted)
                if(_stream == None):
                    _deletedData["DanglingQueueStreamId"].append(_id)
                    
            for _id in _playlist.streamSourceIds:
                _source = self.streamSourceService.get(_id, removeSoftDeleted)
                if(_source == None):
                    _deletedData["DanglingStreamSourceId"].append(_id)
        
        printS("\nPurge summary, the following data will be", (" PERMANENTLY REMOVED" if permanentlyDelete else " DELETED"), " :", color = colors["WARNING"])
        
        printS("\nQueueStream", color = colors["BOLD"])
        printS("No nQueueStreams will be", (" permanently" if permanentlyDelete else ""), " removed", doPrint = len(_deletedData["QueueStream"]) == 0)
        for _ in _deletedData["QueueStream"]:
            print(_.id + " - " + _.name)
            
        printS("\nStreamSource", color = colors["BOLD"])
        printS("No nStreamSources will be removed", doPrint = len(_deletedData["StreamSource"]) == 0)
        for _ in _deletedData["StreamSource"]:
            print(_.id + " - " + _.name)
            
        printS("\nDangling QueueStream IDs", color = colors["BOLD"])
        printS("No IDs will be removed", doPrint = len(_deletedData["DanglingQueueStreamId"]) == 0)
        for _ in _deletedData["DanglingQueueStreamId"]:
            print(_.id + " - " + _.name)
            
        printS("\nDangling StreamSource IDs", color = colors["BOLD"])
        printS("No IDs will be removed", doPrint = len(_deletedData["DanglingStreamSourceId"]) == 0)
        for _ in _deletedData["DanglingStreamSourceId"]:
            print(_.id + " - " + _.name)
        
        printS("Removing ", len(_deletedData["QueueStream"]), " unlinked QueueStreams, ", len(_deletedData["StreamSource"]), " StreamSources.")
        printS("Removing ", len(_deletedData["DanglingQueueStreamId"]), " dangling QueueStream IDs, ", len(_deletedData["DanglingStreamSourceId"]), " dangling StreamSource IDs.")
        printS("Do you want to", (" PERMANENTLY REMOVE" if permanentlyDelete else " DELETE"), " this data?", color = colors["WARNING"])
        _input = input("(y/n):")
        if(_input in affirmative):
            printS("TODO purge", color = colors["OKGREEN"])
            for _ in _deletedData["QueueStream"]:
                if(permanentlyDelete):
                    self.queueStreamService.remove(_.id)
                else:
                    self.queueStreamService.delete(_.id)
                    
            for _ in _deletedData["StreamSource"]:
                if(permanentlyDelete):
                    self.streamSourceService.remove(_.id)
                else:
                    self.streamSourceService.delete(_.id)
            
            
            
            
            return _deletedData
            
        printS("Purge aborted by user.", color = colors["WARNING"])
        return {"QueueStream": [], "StreamSource": []}