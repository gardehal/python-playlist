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
    storagePath: str = LOCAL_STORAGE_PATH
    playlistRepository: LocalJsonRepository = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    utility: Utility = None

    def __init__(self):
        self.playlistRepository: LocalJsonRepository = LocalJsonRepository(T, DEBUG, os.path.join(self.storagePath, "Playlist"))
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
            printS("DEBUG: get - Playlist with ID ", _entity.id, " was soft deleted.", color = colors["WARNING"], doPrint = DEBUG)
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
                printS("DEBUG: getAll - Playlist with ID ", _entity.id, " was soft deleted.", color=colors["WARNING"], doPrint = DEBUG)
            else:
                _result.append(_entity)
            
        return _result
        
    def getAllIds(self, includeSoftDeleted: bool = False) -> List[str]:
        """
        Get all IDs of playlists.

        Args:
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[str]: playlists IDs if any, else empty list
        """
        
        _all = self.getAll(includeSoftDeleted)
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
        
    def restore(self, id: str) -> T:
        """
        Restore a (soft) deleted Playlist.

        Args:
            id (str): ID of Playlist to restore

        Returns:
            Playlist | None: returns Playlist if success, else None
        """

        _entity = self.get(id, includeSoftDeleted = True)
        if(_entity == None):
            return None

        _entity.deleted = None
        _result = self.update(_entity)
        if(_result):
            return _entity
        else:
            return None
        
    def remove(self, id: str, includeSoftDeleted: bool = False) -> T:
        """
        Permanently remove a Playlist.

        Args:
            id (str): ID of Playlist to remove
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            Playlist | None: returns Playlist if success, else None
        """

        _entity = self.get(id, includeSoftDeleted)
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
        (Soft) Delete QueueStreams from Playlist.

        Args:
            playlistId (str): ID of Playlist to remove from
            streamIds (List[str]): IDs of QueueStreams to remove

        Returns:
            List[QueueStream]: QueueStream deleted
        """

        _return = []
        _playlist = self.get(playlistId)
        if(_playlist == None):
            return _return

        for id in streamIds:
            _stream = self.queueStreamService.get(id)
            if(_stream == None):
                continue
            
            _removeResult = self.queueStreamService.delete(id)
            if(_removeResult != None):
                _playlist.streamIds.remove(_stream.id)
                _return.append(_stream)

        _updateResult = self.update(_playlist)
        if(_updateResult):
            return _return
        else:
            return []
        
    def restoreStreams(self, playlistId: str, streamIds: List[str]) -> List[QueueStream]:
        """
        Restore QueueStreams to Playlist.

        Args:
            playlistId (str): ID of Playlist to restore to
            streamIds (List[str]): IDs of QueueStreams to restore

        Returns:
            List[QueueStream]: QueueStream restored
        """

        _return = []
        _playlist = self.get(playlistId, includeSoftDeleted = True)
        if(_playlist == None):
            return _return

        for id in streamIds:
            _stream = self.queueStreamService.get(id, includeSoftDeleted = True)
            if(_stream == None):
                continue
            
            _result = self.queueStreamService.restore(id)
            if(_result != None):
                _playlist.streamIds.append(_stream.id)
                _return.append(_stream)

        _updateResult = self.update(_playlist)
        if(_updateResult):
            return _return
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
            printS("DEBUG: moveStream - Index from and to were the same. No update needed.", color=colors["WARNING"], doPrint = DEBUG)
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
    
    def deleteStreamSources(self, playlistId: str, streamSourceIds: List[str]) -> List[StreamSource]:
        """
        (Soft) Delete StreamSources from Playlist.

        Args:
            playlistId (str): ID of Playlist to delete from
            streamSourceIds (List[str]): IDs of StreamSources to delete

        Returns:
            List[StreamSource]: StreamSources deleted
        """

        _return = []
        _playlist = self.get(playlistId)
        if(_playlist == None):
            return _return

        for id in streamSourceIds:
            _source = self.streamSourceService.get(id)
            if(_source == None):
                continue
            
            _removeResult = self.streamSourceService.delete(id)
            if(_removeResult != None):
                _playlist.streamSourceIds.remove(_source.id)
                _return.append(_source)

        _updateResult = self.update(_playlist)
        if(_updateResult):
            return _return
        else:
            return []
        
    def restoreStreamSources(self, playlistId: str, streamSourceIds: List[str]) -> List[StreamSource]:
        """
        Restore StreamSources to Playlist.

        Args:
            playlistId (str): ID of Playlist to restore to
            streamSourceIds (List[str]): IDs of StreamSources to restore

        Returns:
            List[StreamSource]: StreamSource restored
        """

        _return = []
        _playlist = self.get(playlistId, includeSoftDeleted = True)
        if(_playlist == None):
            return _return

        for id in streamSourceIds:
            _source = self.streamSourceService.get(id, includeSoftDeleted = True)
            if(_source == None):
                continue
            
            _result = self.streamSourceService.restore(id)
            if(_result != None):
                _playlist.streamSourceIds.append(_source.id)
                _return.append(_source)

        _updateResult = self.update(_playlist)
        if(_updateResult):
            return _return
        else:
            return []

    def getStreamsByPlaylistId(self, playlistId: str, includeSoftDeleted: bool = False) -> List[QueueStream]:
        """
        Get all QueueStreams in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to add to
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[QueueStream]: QueueStreams if any, else empty list
        """

        _playlist = self.get(playlistId, includeSoftDeleted)
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

        _playlist = self.get(playlistId, includeSoftDeleted)
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
    
    def getSourcesByPlaylistId(self, playlistId: str, getFetchEnabledOnly: bool = False, includeSoftDeleted: bool = False) -> List[StreamSource]:
        """
        Get StreamSources in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to get from
            includeSoftDeleted (bool): should include soft-deleted entities

        Returns:
            List[StreamSource]: StreamSources if any, else empty list
        """

        _playlist = self.get(playlistId, includeSoftDeleted)
        if(_playlist == None):
            return 0

        _playlistSources = []
        for id in _playlist.streamSourceIds:
            _source = self.streamSourceService.get(id, includeSoftDeleted)
            if(_source == None):
                printS("A StreamSource with ID: ", id, " was listed in Playlist \"", _playlist.name, "\", but was not found in the database. Consider removing it by running the purge command.", color = colors["WARNING"])
                continue
            
            if(getFetchEnabledOnly and not _source.enableFetch):
                continue
                
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

        _playlist = self.get(playlistId, includeSoftDeleted)
        if(_playlist == None or _playlist.playWatchedStreams):
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
        
        _updateResult = self.update(_playlist)
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
        _playlists = self.getAll(includeSoftDeleted)
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
            self.update(_playlist)
            
        return _deletedData
      
    def printPlaylistDetails(self, playlistIds: List[str], includeUri: bool = False, includeId: bool = False, includeDatetime: bool = False, includeListCount: bool = False) -> int:
        """
        Print detailed info for Playlist, including details for related StreamSources and QueueStreams.

        Args:
            playlistIds (List[str]): list of playlistIds to print details of
            includeUri (bool, optional): should print include URI if any. Defaults to False
            includeId (bool, optional): should print include IDs. Defaults to False
            
        Returns:
            int: number of playlists printed for
        """
        
        _result = 0
        for _id in playlistIds:
            _playlist = self.get(_id)
              
            _playlistDetailsString = _playlist.detailsString(includeUri, includeId, includeDatetime, includeListCount = False)
            if(includeListCount):
                _unwatchedStreams = self.getUnwatchedStreamsByPlaylistId(_playlist.id)
                _fetchedSources = self.getSourcesByPlaylistId(_playlist.id, getFetchEnabledOnly = True)
                _sourcesListString = f", unwatched streams: {len(_unwatchedStreams)}/{len(_playlist.streamIds)}"
                _streamsListString = f", fetched sources: {len(_fetchedSources)}/{len(_playlist.streamSourceIds)}"
                _playlistDetailsString += _sourcesListString + _streamsListString

            printS(_playlistDetailsString)
            
            printS("\tStreamSources", color = colors["BOLD"])
            if(len(_playlist.streamSourceIds) == 0):
                printS("\tNo sources added yet.")
            
            for i, _sourceId in enumerate(_playlist.streamSourceIds):
                _source = self.streamSourceService.get(_sourceId)
                if(_source == None):
                    printS("\\tSource not found (ID: \"", _sourceId, "\").", color = colors["FAIL"])
                    continue
                
                _color = "WHITE" if i % 2 == 0 else "GREYBG"
                printS("\t", str(i), " - ", _source.detailsString(includeUri, includeId, includeDatetime, includeListCount), color = colors[_color])
            
            print("\n")
            printS("\tQueueStreams", color = colors["BOLD"])
            if(len(_playlist.streamIds) == 0):
                printS("\tNo streams added yet.")
            
            for i, _streamId in enumerate(_playlist.streamIds):
                _stream = self.queueStreamService.get(_streamId)
                if(_stream == None):
                    printS("\tStream not found (ID: \"", _streamId, "\").", color = colors["FAIL"])
                    continue
                
                _color = "WHITE" if i % 2 == 0 else "GREYBG"
                printS("\t", str(i), " - ", _stream.detailsString(includeUri, includeId, includeDatetime, includeListCount), color = colors[_color])
                
            _result += 1
                
        return _result