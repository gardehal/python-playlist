import os
import re
from typing import List

import mechanize
from enums.StreamSourceType import StreamSourceType, StreamSourceTypeUtil
from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTimeAsNumber
from grdUtil.FileUtil import mkdir
from grdUtil.InputUtil import sanitize
from grdUtil.PrintUtil import printD, printS
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource
from pytube import YouTube
from Settings import Settings

from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.StreamSourceService import StreamSourceService


class SharedService():
    settings: Settings = None
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None

    def __init__(self):
        self.settings = Settings()
        self.playlistService: PlaylistService = PlaylistService()
        self.queueStreamService: QueueStreamService = QueueStreamService()
        self.streamSourceService: StreamSourceService = StreamSourceService()

    def getPageTitle(self, url: str) -> str:
        """
        Get page title from the URL url, using mechanize or PyTube.

        Args:
            url (str): URL to page to get title from.

        Returns:
            str: Title of page.
        """
        
        isYouTubeChannel = "user" in url or "channel" in url
        title = None
        if(StreamSourceTypeUtil.strToStreamSourceType(url) == StreamSourceType.YOUTUBE and not isYouTubeChannel):
            printD(" Getting title from pytube.", color = BashColor.WARNING, doPrint = self.settings.debug)
            yt = YouTube(url)
            title = yt.title
        else:
            printD("Getting title from mechanize.", color = BashColor.WARNING, doPrint = self.settings.debug)
            try:
                br = mechanize.Browser()
                br.open(url)
                title = br.title()
                br.close()
            except Exception as e:
                printS(f"Could not fetch name from URL {url}:\n{e}", color = BashColor.FAIL)
                return None

        return sanitize(title).strip()

    def preparePrune(self, playlistId: str, includeSoftDeleted: bool = False) -> dict[list[Playlist], list[QueueStream]]:
        """
        Prepare a prune to permanently remove all soft-deleted entities, getting data for doPrune.
        
        Args:
            playlistId (str): ID of playlist to prune.
            includeSoftDeleted (bool, optional): Should include soft-deleted entities. Defaults to False.
            
        Returns:
            dict[list[Playlist], list[QueueStream]]: Entities to remove.
        """
        
        dataEmpty = { "Playlist": [], "QueueStream": []}
        data = dataEmpty.copy()

        playlist = self.playlistService.get(playlistId, includeSoftDeleted)
        if(playlist == None or playlist.playWatchedStreams):
            return dataEmpty
        
        for id in playlist.streamIds:
            stream = self.queueStreamService.get(id, includeSoftDeleted)
            if(stream != None and stream.watched != None):
                data["QueueStream"].append(stream)
        
        if(len(data["QueueStream"]) > 0):
            data["Playlist"].append(playlist)
        
        return data
    
    def doPrune(self, data: dict[list[Playlist], list[QueueStream]], includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> bool:
        """
        Prune (permanently remove/soft delete) watched QueueStreams from Playlists given as data.
        
        Args:
            dict[list[Playlist], list[QueueStream]]): Data to remove.
            includeSoftDeleted (bool): Should soft-deleted entities be deleted.
            permanentlyDelete (bool): Should entities be permanently deleted.
            
        Returns:
            bool: Result.
        """
        
        for stream in data["QueueStream"]:
            if(permanentlyDelete):
                self.queueStreamService.remove(stream.id, includeSoftDeleted)
            else:
                self.queueStreamService.delete(stream.id)
                
            for playlist in data["Playlist"]:
                playlist.streamIds.remove(stream.id)
                result = self.playlistService.update(playlist)
                if(not result):
                    printD("failed to update Playlist \"", playlist.name, "\".", color = BashColor.WARNING, doPrint = self.settings.debug)
                    return False
                    
        return True
    
    def preparePurge(self) -> dict[list[QueueStream], list[StreamSource], list[Playlist]]:
        """
        Prepare a purge to permanently remove all soft-deleted entities, getting data for doPurge.
            
        Returns:
            dict[list[QueueStream], list[StreamSource], list[Playlist]]: Entities to remove.
        """
        
        dataEmpty = {"QueueStream": [], "StreamSource": [], "Playlist": []}
        data = dataEmpty.copy()
        
        allQ = self.queueStreamService.getAll(includeSoftDeleted = True)
        data["QueueStream"] = [_ for _ in allQ if _.deleted != None]
        allS = self.streamSourceService.getAll(includeSoftDeleted = True)
        data["StreamSource"] = [_ for _ in allS if _.deleted != None]
        allP = self.playlistService.getAll(includeSoftDeleted = True)
        data["Playlist"] = [_ for _ in allP if _.deleted != None]
        
        return data
    
    def doPurge(self, data: dict[list[QueueStream], list[StreamSource], list[Playlist]]) -> bool:
        """
        Purge (permanently remove) all soft-deleted entities given as data.
            
        Args:
            data (dict[list[QueueStream], list[StreamSource], list[Playlist]]): Data to remove.
            
        Returns:
            bool: Result.
        """
        
        for _ in data["QueueStream"]:
            self.queueStreamService.remove(_.id, True)
        for _ in data["StreamSource"]:
            self.streamSourceService.remove(_.id, True)
        for _ in data["Playlist"]:
            self.playlistService.remove(_.id, True)
            
        return True
    
    def preparePurgePlaylists(self, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> dict[list[QueueStream], list[StreamSource], list[Playlist]]:
        """
        Prepare a purge to delete/permanently remove QueueStreams and StreamSources from DB, while removing IDs with no entity from Playlists, getting data for doPurgePlaylists.
        
        Args:
            includeSoftDeleted (bool): Should soft-deleted entities be deleted.
            permanentlyDelete (bool): Should entities be permanently deleted.
            
        Returns:
            dict[list[QueueStream], list[StreamSource], list[Playlist]]: Entities to remove.
        """
        
        dataEmpty = {"QueueStream": [], "StreamSource": [], "Playlist": []}
        data = dataEmpty.copy()
        playlists = self.playlistService.getAll(includeSoftDeleted)
        qIds = self.queueStreamService.getAllIds(includeSoftDeleted)
        sIds = self.streamSourceService.getAllIds(includeSoftDeleted)
        
        allPlaylistQueueStreamIds = []
        allPlaylistStreamStreamIds = []
        for playlist in playlists:
            allPlaylistQueueStreamIds.extend(playlist.streamIds)
            allPlaylistStreamStreamIds.extend(playlist.streamSourceIds)
        
        unlinkedPlaylistQueueStreamIds = [_ for _ in qIds if(_ not in allPlaylistQueueStreamIds)]
        unlinkedPlaylistStreamStreamIds = [_ for _ in sIds if(_ not in allPlaylistStreamStreamIds)]
        
        # Find unlinked QueueStreams and StreamSources (not found in any Playlists)
        for id in unlinkedPlaylistQueueStreamIds:
            if(not id in allPlaylistQueueStreamIds):
                entity = self.queueStreamService.get(id, includeSoftDeleted)
                data["QueueStream"].append(entity)
        for id in unlinkedPlaylistStreamStreamIds:
            if(not id in allPlaylistStreamStreamIds):
                entity = self.streamSourceService.get(id, includeSoftDeleted)
                data["StreamSource"].append(entity)
        
        # Find IDs in Playlists with no corresponding entity
        for playlist in playlists:
            for id in playlist.streamIds:
                if(not self.queueStreamService.exists(id)):
                    data["Playlist"].append(playlist)
                    break
                
            for id in playlist.streamSourceIds:
                if(not self.streamSourceService.exists(id)):
                    data["Playlist"].append(playlist)
                    break
                
        return data
    
    def doPurgePlaylists(self, data: dict[list[Playlist]]) -> bool:
        """
        Purge Playlists given as data for dangling IDs.
            
        Args:
            data (dict[list[Playlist]]): Data to remove where Playlist-list is Playlists to update, and str-list are IDs to remove from any field in Playlists.
            
        Returns:
            bool: Result.
        """
        
        for playlist in data["Playlist"]:
            updatedStreamIds = []
            updatedStreamSourceService = []
            
            for id in playlist.streamIds:
                if(self.queueStreamService.exists(id)):
                    updatedStreamIds.append(id)
                    
            for id in playlist.streamSourceIds:
                if(self.streamSourceService.exists(id)):
                    updatedStreamSourceService.append(id)
                
            playlist.streamIds = updatedStreamIds
            playlist.streamSourceIds = updatedStreamSourceService
            
            self.playlistService.update(playlist)
            
        return True

    def search(self, searchTerm: str, includeSoftDeleted: bool = False) -> dict[List[QueueStream], List[StreamSource], List[Playlist]]:
        """
        Search names and URIs for Regex-term searchTerm and returns a dict with results.

        Args:
            searchTerm (str): Regex-enabled term to search for.
            includeSoftDeleted (bool, optional): Should include soft deleted entities. Defaults to False.

        Returns:
            dict[List[QueueStream], List[StreamSource], List[Playlist]]: Entities that matched the searchTerm.
        """
        
        dataEmpty = {"QueueStream": [], "StreamSource": [], "Playlist": []}
        data = dataEmpty.copy()
        
        queueStreams = self.queueStreamService.getAll(includeSoftDeleted)
        streamSources = self.streamSourceService.getAll(includeSoftDeleted)
        playlists = self.playlistService.getAll(includeSoftDeleted)
        
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
        printD("no results", color = BashColor.WARNING, doPrint = self.settings.debug and not found)
        
        return data 
    
    def searchFields(self, searchTerm: str, *fields) -> int:
        """
        Searches *fields for Regex-enabled searchTerm.

        Args:
            searchTerm (str): Regex-enabled term to search for.
            fields (any): Fields to search.

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
            dict[List[QueueStream], List[StreamSource], List[Playlist]]: Entities that matched the searchTerm.
        """
        
        dataEmpty = {"QueueStream": [], "StreamSource": [], "Playlist": []}
        data = dataEmpty.copy()
        
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

    def downloadYoutube(self, url: str, fileExtension: str = "mp4") -> str:
        """
        Download a Youtube video to given directory.

        Args:
            url (str): URL to video to download.

        Returns:
            str: Absolute path of file.
        """
        
        videoDir = os.path.join(self.settings.localStoragePath, "video", "youtube")
        mkdir(videoDir)
        
        youtube = YouTube(url)
        videoFilename = f"{str(getDateTimeAsNumber())}_{sanitize(youtube.title)}.{fileExtension}".replace(" ", "_").lower()
        youtube.streams.filter(progressive = True, file_extension = fileExtension).order_by("resolution").desc().first().download(videoDir, videoFilename)
                
        return os.path.join(videoDir, videoFilename)
    