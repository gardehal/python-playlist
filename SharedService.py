import os
import re
from typing import List

import mechanize
from dotenv import load_dotenv
from grdUtil.BashColor import BashColor
from grdUtil.InputUtil import sanitize
from grdUtil.PrintUtil import printS
from grdUtil.StaticUtil import StaticUtil
from pytube import YouTube

from enums.StreamSourceType import StreamSourceType, StreamSourceTypeUtil
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource
from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService
from StreamSourceService import StreamSourceService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")
LOG_WATCHED = eval(os.environ.get("LOG_WATCHED"))
DOWNLOAD_WEB_STREAMS = eval(os.environ.get("DOWNLOAD_WEB_STREAMS"))
REMOVE_WATCHED_ON_FETCH = eval(os.environ.get("REMOVE_WATCHED_ON_FETCH"))
PLAYED_ALWAYS_WATCHED = eval(os.environ.get("PLAYED_ALWAYS_WATCHED"))
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")
BROWSER_BIN = os.environ.get("BROWSER_BIN")

class SharedService():
    storagePath: str = LOCAL_STORAGE_PATH
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None

    def __init__(self):
        self.playlistService: PlaylistService = PlaylistService()
        self.queueStreamService: QueueStreamService = QueueStreamService()
        self.streamSourceService: StreamSourceService = StreamSourceService()

    def getPageTitle(self, url: str) -> str:
        """
        Get page title from the URL url, using mechanize or PyTube.

        Args:
            url (str): URL to page to get title from

        Returns:
            str: Title of page
        """
        
        isYouTubeChannel = "user" in url or "channel" in url  
        if(StreamSourceTypeUtil.strToStreamSourceType(url) == StreamSourceType.YOUTUBE and not isYouTubeChannel):
            printS("DEBUG: getPageTitle - Getting title from pytube.", color = BashColor.WARNING, doPrint = DEBUG)
            yt = YouTube(url)
            title = yt.title
        else:
            printS("DEBUG: getPageTitle - Getting title from mechanize.", color = BashColor.WARNING, doPrint = DEBUG)
            br = mechanize.Browser()
            br.open(url)
            title = br.title()
            br.close()

        return sanitize(title).strip()

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
        
        deletedDataEmpty = {"QueueStream": [], "QueueStreamId": []}
        deletedData = deletedDataEmpty

        playlist = self.playlistService.get(playlistId, includeSoftDeleted)
        if(playlist == None or playlist.playWatchedStreams):
            return deletedDataEmpty
        
        for id in playlist.streamIds:
            stream = self.queueStreamService.get(id, includeSoftDeleted)
            if(stream != None and stream.watched != None):
                deletedData["QueueStream"].append(stream)
            
        # Will not do anything if streams already deleted
        for stream in deletedData["QueueStream"]:
            deletedData["QueueStreamId"].append(stream.id)
            
        printS("\nPrune summary, the following data will be", (" PERMANENTLY REMOVED" if permanentlyDelete else " DELETED"), ":", color = BashColor.WARNING)
            
        printS("\nQueueStream(s)", color = BashColor.BOLD)
        printS("No QueueStreams will be removed", doPrint = len(deletedData["QueueStream"]) == 0)
        for stream in deletedData["QueueStream"]:
            print(stream.id + " - " + stream.name)
            
        printS("\nQueueStream ID(s)", color = BashColor.BOLD)
        printS("No IDs will be removed", doPrint = len(deletedData["QueueStreamId"]) == 0)
        for id in deletedData["QueueStreamId"]:
            print(id)
            
        printS("\nRemoving ", len(deletedData["QueueStream"]), " watched QueueStream(s) and ", len(deletedData["QueueStreamId"]), " ID(s) in Playlist \"", playlist.name, "\".")
        printS("Do you want to", (" PERMANENTLY REMOVE" if permanentlyDelete else " DELETE"), " this data?", color = BashColor.WARNING)
        inputArgs = input("(y/n):")
        if(inputArgs not in StaticUtil.affirmative):
            printS("Prune aborted by user.", color = BashColor.WARNING)
            return deletedDataEmpty
        
        if(len(deletedData["QueueStream"]) == 0 and len(deletedData["QueueStreamId"]) == 0):
            printS("No data was available.", color = BashColor.WARNING)
            return deletedDataEmpty
        
        printS("DEBUG: prune - remove streams", color = BashColor.WARNING, doPrint = DEBUG)
        for stream in deletedData["QueueStream"]:
            if(permanentlyDelete):
                self.queueStreamService.remove(stream.id, includeSoftDeleted)
            else:
                self.queueStreamService.delete(stream.id)
                
            playlist.streamIds.remove(stream.id)
        
        updateResult = self.playlistService.update(playlist)
        if(updateResult != None):
            return deletedData
        else:
            return deletedDataEmpty
    
    def purge(self) -> dict[List[QueueStream], List[StreamSource], List[Playlist]]:
        """
        Purges deleted entities.
            
        Returns:
            dict[List[QueueStream], List[StreamSource], List[Playlist]]: dict with three lists, StreamSources removed, QueueStreams removed, Playlists removed from playlists
        """
        deletedDataEmpty = {"QueueStream": [], "StreamSource": [], "Playlist": []}
        return deletedDataEmpty
        
    def purgePlaylists(self, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> dict[List[QueueStream], List[StreamSource], List[str], List[str]]:
        """
        Purges the dangling IDs from Playlists, and purge unlinked StreamSources and QueueStreams.

        Args:
            includeSoftDeleted (bool): should soft-deleted entities be deleted
            permanentlyDelete (bool): should entities be permanently deleted
            
        Returns:
            dict[List[QueueStream], List[StreamSource], List[str], List[str]]: dict with four lists, one for StreamSources removed, QueueStreams removed, QueueStreamId removed from playlists, and StreamSourceId removed
        """
        
        deletedDataEmpty = {"QueueStream": [], "StreamSource": [], "QueueStreamId": [], "StreamSourceId": []}
        deletedData = deletedDataEmpty
        playlists = self.playlistService.getAll(includeSoftDeleted)
        streamsIds = self.queueStreamService.getAllIds(includeSoftDeleted)
        sourcesIds = self.streamSourceService.getAllIds(includeSoftDeleted)
        
        playlistStreams = []
        playlistSources = []
        updatedPlaylists = []
        for playlist in playlists:
            playlistStreams.extend(playlist.streamIds)
            playlistSources.extend(playlist.streamSourceIds)
        
        for id in streamsIds:
            if(not id in playlistStreams):
                entity = self.queueStreamService.get(id, includeSoftDeleted)
                deletedData["QueueStream"].append(entity)
        for id in sourcesIds:
            if(not id in playlistSources):
                entity = self.streamSourceService.get(id, includeSoftDeleted)
                deletedData["StreamSource"].append(entity)
                
        for playlist in playlists:
            streamIdsToRemove = []
            sourceIdsToRemove = []
            
            for id in playlist.streamIds:
                stream = self.queueStreamService.get(id, includeSoftDeleted)
                if(stream == None):
                    streamIdsToRemove.append(id)
                    
            for id in playlist.streamSourceIds:
                source = self.streamSourceService.get(id, includeSoftDeleted)
                if(source == None):
                    sourceIdsToRemove.append(id)
                    
            if(len(streamIdsToRemove) > 0 or len(sourceIdsToRemove) > 0):
                for id in streamIdsToRemove:
                    playlist.streamIds.remove(id)
                for id in sourceIdsToRemove:
                    playlist.streamSourceIds.remove(id)
                
                updatedPlaylists.append(playlist)
        
        printS("\nPurge summary, the following data will be", (" PERMANENTLY REMOVED" if permanentlyDelete else " DELETED"), ":", color = BashColor.WARNING)
        
        printS("\nQueueStream(s)", color = BashColor.BOLD)
        printS("No QueueStream(s) will be", (" permanently" if permanentlyDelete else ""), " removed", doPrint = len(deletedData["QueueStream"]) == 0)
        for _ in deletedData["QueueStream"]:
            print(_.id + " - " + _.name)
            
        printS("\nStreamSource(s)", color = BashColor.BOLD)
        printS("No StreamSource(s) will be removed", doPrint = len(deletedData["StreamSource"]) == 0)
        for _ in deletedData["StreamSource"]:
            print(_.id + " - " + _.name)
            
        printS("\nDangling QueueStream ID(s)", color = BashColor.BOLD)
        printS("No ID(s) will be removed", doPrint = len(deletedData["QueueStreamId"]) == 0)
        for _ in deletedData["QueueStreamId"]:
            print(_.id + " - " + _.name)
            
        printS("\nDangling StreamSource ID(s)", color = BashColor.BOLD)
        printS("No ID(s) will be removed", doPrint = len(deletedData["StreamSourceId"]) == 0)
        for _ in deletedData["StreamSourceId"]:
            print(_.id + " - " + _.name)
        
        printS("\nRemoving ", len(deletedData["QueueStream"]), " unlinked QueueStream(s), ", len(deletedData["StreamSource"]), " unlinked StreamSource(s).")
        printS("Removing ", len(deletedData["QueueStreamId"]), " dangling QueueStream ID(s), ", len(deletedData["StreamSourceId"]), " dangling StreamSource ID(s).")
        printS("Do you want to", (" PERMANENTLY REMOVE" if permanentlyDelete else " DELETE"), " this data?", color = BashColor.WARNING)
        inputArgs = input("(y/n):")
        if(inputArgs not in StaticUtil.affirmative):
            printS("Purge aborted by user.", color = BashColor.WARNING)
            return deletedDataEmpty
            
        if(len(deletedData["QueueStream"]) == 0 and len(deletedData["StreamSource"]) == 0 and len(deletedData["QueueStreamId"]) == 0 and len(deletedData["StreamSourceId"]) == 0):
            printS("No data was available.", color = BashColor.WARNING)
            return deletedDataEmpty
            
        for _ in deletedData["QueueStream"]:
            if(permanentlyDelete):
                self.queueStreamService.remove(_.id, includeSoftDeleted)
            else:
                self.queueStreamService.delete(_.id)
                
        for _ in deletedData["StreamSource"]:
            if(permanentlyDelete):
                self.streamSourceService.remove(_.id, includeSoftDeleted)
            else:
                self.streamSourceService.delete(_.id)
        
        for playlist in updatedPlaylists:
            self.playlistService.update(playlist)
            
        return deletedData
    
    def search(self, searchTerm: str, includeSoftDeleted: bool = False) -> dict[List[QueueStream], List[StreamSource], List[Playlist]]:
        """
        Search names and URIs for Regex-term searchTerm and returns a dict with results.

        Args:
            searchTerm (str): Regex-enabled term to search for
            includeSoftDeleted (bool, optional): Should include soft deleted entities. Defaults to False.

        Returns:
            dict[List[QueueStream], List[StreamSource], List[Playlist]]: A dict of lists with entities that matched the searchTerm
        """
        
        dataEmpty = {"QueueStream": [], "StreamSource": [], "Playlist": []}
        data = dataEmpty
        
        queueStreams = self.queueStreamService.getAll()
        streamSources = self.streamSourceService.getAll()
        playlists = self.playlistService.getAll()
        
        for entity in queueStreams:
            if(self.searchFields(searchTerm, entity.name, entity.uri) > 0):
                data["QueueStream"].append(entity)
        for entity in streamSources:
            if(self.searchFields(searchTerm, entity.name, entity.uri) > 0):
                data["StreamSource"].append(entity)
        for entity in playlists:
            if(self.searchFields(searchTerm, entity.name) > 0):
                data["Playlist"].append(entity)
        
        found = len(data["QueueStream"]) > 0 or len(data["StreamSource"]) > 0 or len(data["Playlist"]) > 0
        printS("DEBUG: search - no results", color = BashColor.WARNING, doPrint = DEBUG and not found)
        
        return data 
    
    def searchFields(self, searchTerm: str, *fields) -> int:
        """
        Searchs *fields for Regex-enabled searchTerm.

        Args:
            searchTerm (str): Regex-enabled term to search for
            fields (any): fields to search

        Returns:
            int: int of field first found in, 0 = not found, 1 = first field-argument etc.
        """
        
        for i, field in enumerate(fields):
            if(re.search(searchTerm, field, re.IGNORECASE)):
                return i + 1
        
        return 0
    
    def getAllSoftDeleted(self) -> dict[List[QueueStream], List[StreamSource], List[Playlist]]:
        """
        Returns a dict with lists of all soft deleted entities.

        Returns:
            dict[List[QueueStream], List[StreamSource], List[Playlist]]: A dict of lists with entities that matched the searchTerm
        """
        
        dataEmpty = {"QueueStream": [], "StreamSource": [], "Playlist": []}
        data = dataEmpty
        
        queueStreams = self.queueStreamService.getAll(includeSoftDeleted = True)
        streamSources = self.streamSourceService.getAll(includeSoftDeleted = True)
        playlists = self.playlistService.getAll(includeSoftDeleted = True)
        
        for entity in queueStreams:
            if(entity.deleted != None):
                data["QueueStream"].append(entity)
        for entity in streamSources:
            if(entity.deleted != None):
                data["StreamSource"].append(entity)
        for entity in playlists:
            if(entity.deleted != None):
                data["Playlist"].append(entity)
        
        return data
