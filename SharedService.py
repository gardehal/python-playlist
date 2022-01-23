import os
from typing import List

from dotenv import load_dotenv
from myutil.Util import *
import pytube
from PlaylistService import PlaylistService

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

affirmative = ["yes", "y", "1"]
negative = ["no", "n", "0"]

class SharedService():
    debug: bool = DEBUG
    storagePath: str = LOCAL_STORAGE_PATH
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    utility: Utility = None

    def __init__(self):
        self.playlistService: PlaylistService = PlaylistService()
        self.queueStreamService: QueueStreamService = QueueStreamService()
        self.streamSourceService: StreamSourceService = StreamSourceService()
        self.utility: Utility = Utility()

    def getStreamsByPlaylistId(self, playlistId: str, includeSoftDeleted: bool = False) -> List[QueueStream]:
        """
        Get all QueueStreams in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to add to
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[QueueStream]: QueueStreams if any, else empty list
        """

        _playlist = self.playlistService.get(playlistId, includeSoftDeleted)
        if(_playlist == None):
            return 0

        _playlistStreams = []
        for id in _playlist.streamIds:
            _stream = self.queueStreamService.get(id, includeSoftDeleted)
            if(_stream == None):
                printS("A QueueStream with ID: ", id, " was listed in Playlist \"", _playlist.name, "\", but was not found in the database. Consider removing it by running the purge command.", color = colors["WARNING"])
                continue
            
            _playlistStreams.append(_stream)

        return _playlistStreams
    
    def getUnwatchedStreamsByPlaylistId(self, playlistId: str, includeSoftDeleted: bool = False) -> List[QueueStream]:
        """
        Get unwatched QueueStreams in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to get from
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[QueueStream]: QueueStreams if any, else empty list
        """

        _playlist = self.playlistService.get(playlistId, includeSoftDeleted)
        if(_playlist == None):
            return 0

        _playlistStreams = []
        for id in _playlist.streamIds:
            _stream = self.queueStreamService.get(id, includeSoftDeleted)
            if(_stream == None):
                printS("A QueueStream with ID: ", id, " was listed in Playlist \"", _playlist.name, "\", but was not found in the database. Consider removing it by running the purge command.", color = colors["WARNING"])
                continue
            
            if(_stream.watched == None):
                _playlistStreams.append(_stream)

        return _playlistStreams    
    
    def getFetchedSourcesByPlaylistId(self, playlistId: str, includeSoftDeleted: bool = False) -> List[StreamSource]:
        """
        Get StreamSources where fetch is enabled in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to get from
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[StreamSource]: StreamSources if any, else empty list
        """

        _playlist = self.playlistService.get(playlistId, includeSoftDeleted)
        if(_playlist == None):
            return 0

        _playlistSources = []
        for id in _playlist.streamSourceIds:
            _source = self.streamSourceService.get(id, includeSoftDeleted)
            if(_source == None):
                printS("A StreamSource with ID: ", id, " was listed in Playlist \"", _playlist.name, "\", but was not found in the database. Consider removing it by running the purge command.", color = colors["WARNING"])
                continue
            
            if(_source.enableFetch == True):
                _playlistSources.append(_source)

        return _playlistSources

    def prune(self, playlistId: str, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> dict[List[QueueStream], List[str]]:
        """
        Removes watched streams from a Playlist if it does not allow replaying of already played streams (playWatchedStreams == False).

        Args:
            playlistId (str): ID of playlist to prune
            includeSoftDeleted (bool): should include soft-deleted entities
            permanentlyDelete (bool): should entities be permanently deleted

        Returns:
            dict[List[QueueStream], List[str]]: dict with two lists, for StreamSources removed from database, StreamSourceId removed from playlist
        """
        
        _deletedDataEmpty = {"QueueStream": [], "QueueStreamId": []}
        _deletedData = _deletedDataEmpty

        _playlist = self.playlistService.get(playlistId, includeSoftDeleted)
        if(_playlist == None or _playlist.playWatchedStreams == True):
            return _deletedDataEmpty
        
        for _id in _playlist.streamIds:
            _stream = self.queueStreamService.get(_id, includeSoftDeleted)
            if(_stream != None and _stream.watched != None):
                _deletedData["QueueStream"].append(_stream)
            
        # Will not do anything if streams already deleted
        for _stream in _deletedData["QueueStream"]:
            _deletedData["QueueStreamId"].append(_stream.id)
            
        printS("\nPrune summary, the following data will be", (" PERMANENTLY REMOVED" if permanentlyDelete else " DELETED"), ":", color = colors["WARNING"])
            
        printS("\QueueStream", color = colors["BOLD"])
        printS("No QueueStreams will be removed", doPrint = len(_deletedData["QueueStream"]) == 0)
        for _stream in _deletedData["QueueStream"]:
            print(_stream.id + " - " + _stream.name)
            
        printS("\nQueueStream IDs", color = colors["BOLD"])
        printS("No IDs will be removed", doPrint = len(_deletedData["QueueStreamId"]) == 0)
        for _id in _deletedData["QueueStreamId"]:
            print(_id)
            
        printS("\nRemoving ", len(_deletedData["QueueStream"]), " watched QueueStreams and ", len(_deletedData["QueueStreamId"]), " IDs in Playlist \"", _playlist.name, "\".")
        printS("Do you want to", (" PERMANENTLY REMOVE" if permanentlyDelete else " DELETE"), " this data?", color = colors["WARNING"])
        _input = input("(y/n):")
        if(_input not in affirmative):
            printS("Prune aborted by user.", color = colors["WARNING"])
            return _deletedDataEmpty
        
        if(len(_deletedData["QueueStream"]) == 0 and len(_deletedData["QueueStreamId"]) == 0):
            printS("No data was available.", color = colors["WARNING"])
            return _deletedDataEmpty
        
        printS("DEBUG: prune - remove streams", color = colors["WARNING"], doPrint = DEBUG)
        for _stream in _deletedData["QueueStream"]:
            if(permanentlyDelete):
                self.queueStreamService.remove(_stream.id, includeSoftDeleted)
            else:
                self.queueStreamService.delete(_stream.id)
                
            _playlist.streamIds.remove(_stream.id)
        
        _updateResult = self.playlistService.update(_playlist)
        if(_updateResult != None):
            return _deletedData
        else:
            return _deletedDataEmpty
        
    def purge(self, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> dict[List[QueueStream], List[StreamSource], List[str], List[str]]:
        """
        Purges the dangling IDs from Playlists, and purge unlinked StreamSources and QueueStreams.

        Args:
            includeSoftDeleted (bool): should soft-deleted entities be deleted
            permanentlyDelete (bool): should entities be permanently deleted
            
        Returns:
            dict[List[QueueStream], List[StreamSource], List[str], List[str]]: dict with four lists, one for StreamSources removed, QueueStreams removed, QueueStreamId removed from playlists, and StreamSourceId removed
        """
        
        _deletedDataEmpty = {"QueueStream": [], "StreamSource": [], "QueueStreamId": [], "StreamSourceId": []}
        _deletedData = _deletedDataEmpty
        _playlists = self.playlistService.getAll(includeSoftDeleted)
        _streamsIds = self.queueStreamService.getAllIds(includeSoftDeleted)
        _sourcesIds = self.streamSourceService.getAllIds(includeSoftDeleted)
        
        _playlistStreams = []
        _playlistSources = []
        _updatedPlaylists = []
        for _playlist in _playlists:
            _playlistStreams.extend(_playlist.streamIds)
            _playlistSources.extend(_playlist.streamSourceIds)
        
        for _id in _streamsIds:
            if(not _id in _playlistStreams):
                _entity = self.queueStreamService.get(_id, includeSoftDeleted)
                _deletedData["QueueStream"].append(_entity)
        for _id in _sourcesIds:
            if(not _id in _playlistSources):
                _entity = self.streamSourceService.get(_id, includeSoftDeleted)
                _deletedData["StreamSource"].append(_entity)
                
        for _playlist in _playlists:
            _streamIdsToRemove = []
            _sourceIdsToRemove = []
            
            for _id in _playlist.streamIds:
                _stream = self.queueStreamService.get(_id, includeSoftDeleted)
                if(_stream == None):
                    _streamIdsToRemove.append(_id)
                    
            for _id in _playlist.streamSourceIds:
                _source = self.streamSourceService.get(_id, includeSoftDeleted)
                if(_source == None):
                    _sourceIdsToRemove.append(_id)
                    
            if(len(_streamIdsToRemove) > 0 or len(_sourceIdsToRemove) > 0):
                for _id in _streamIdsToRemove:
                    _playlist.streamIds.remove(_id)
                for _id in _sourceIdsToRemove:
                    _playlist.streamSourceIds.remove(_id)
                
                _streamIdsToRemove.extend(_deletedData["QueueStreamId"])
                _sourceIdsToRemove.extend(_deletedData["StreamSourceId"])
                _updatedPlaylists.append(_playlist)
        
        printS("\nPurge summary, the following data will be", (" PERMANENTLY REMOVED" if permanentlyDelete else " DELETED"), ":", color = colors["WARNING"])
        
        printS("\nQueueStream", color = colors["BOLD"])
        printS("No QueueStreams will be", (" permanently" if permanentlyDelete else ""), " removed", doPrint = len(_deletedData["QueueStream"]) == 0)
        for _ in _deletedData["QueueStream"]:
            print(_.id + " - " + _.name)
            
        printS("\nStreamSource", color = colors["BOLD"])
        printS("No StreamSources will be removed", doPrint = len(_deletedData["StreamSource"]) == 0)
        for _ in _deletedData["StreamSource"]:
            print(_.id + " - " + _.name)
            
        printS("\nDangling QueueStream IDs", color = colors["BOLD"])
        printS("No IDs will be removed", doPrint = len(_deletedData["QueueStreamId"]) == 0)
        for _ in _deletedData["QueueStreamId"]:
            print(_.id + " - " + _.name)
            
        printS("\nDangling StreamSource IDs", color = colors["BOLD"])
        printS("No IDs will be removed", doPrint = len(_deletedData["StreamSourceId"]) == 0)
        for _ in _deletedData["StreamSourceId"]:
            print(_.id + " - " + _.name)
        
        printS("\nRemoving ", len(_deletedData["QueueStream"]), " unlinked QueueStreams, ", len(_deletedData["StreamSource"]), " StreamSources.")
        printS("Removing ", len(_deletedData["QueueStreamId"]), " dangling QueueStream IDs, ", len(_deletedData["StreamSourceId"]), " dangling StreamSource IDs.")
        printS("Do you want to", (" PERMANENTLY REMOVE" if permanentlyDelete else " DELETE"), " this data?", color = colors["WARNING"])
        _input = input("(y/n):")
        if(_input not in affirmative):
            printS("Purge aborted by user.", color = colors["WARNING"])
            return _deletedDataEmpty
            
        if(len(_deletedData["QueueStream"]) == 0 and len(_deletedData["StreamSource"]) == 0 and len(_deletedData["QueueStreamId"]) == 0 and len(_deletedData["StreamSourceId"]) == 0):
            printS("No data was available.", color = colors["WARNING"])
            return _deletedDataEmpty
            
        for _ in _deletedData["QueueStream"]:
            if(permanentlyDelete):
                self.queueStreamService.remove(_.id, includeSoftDeleted)
            else:
                self.queueStreamService.delete(_.id)
                
        for _ in _deletedData["StreamSource"]:
            if(permanentlyDelete):
                self.streamSourceService.remove(_.id, includeSoftDeleted)
            else:
                self.streamSourceService.delete(_.id)
        
        for _playlist in _updatedPlaylists:
            self.playlistService.update(_playlist)
            
        return _deletedData
      