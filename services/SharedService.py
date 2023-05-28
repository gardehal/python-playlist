import os
import re
from typing import Dict, List

import mechanize
from enums.StreamSourceType import StreamSourceType, StreamSourceTypeUtil
from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTimeAsNumber
from grdUtil.FileUtil import mkdir
from grdUtil.InputUtil import sanitize
from grdUtil.PrintUtil import printD, printS
from model.Playlist import Playlist
from model.PlaylistDetailed import PlaylistDetailed
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
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.streamSourceService = StreamSourceService()

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
        try:
            if(StreamSourceTypeUtil.strToStreamSourceType(url) == StreamSourceType.YOUTUBE and not isYouTubeChannel):
                printD("Getting title from pytube.", color = BashColor.WARNING, debug = self.settings.debug)
                yt = YouTube(url)
                title = yt.title
            else:
                printD("Getting title from mechanize.", color = BashColor.WARNING, debug = self.settings.debug)
                try:
                    br = mechanize.Browser()
                    br.set_handle_robots(False)
                    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
                    br.open(url)
                    title = br.title()
                    br.close()
                except Exception as e:
                    printS(f"Could not fetch name from URL {url}:\n{e}", color = BashColor.FAIL)
                    return None
        except:
            printS(f"Could not get name from source, please try again.", color = BashColor.FAIL)
            return None

        return sanitize(title).strip()

    def preparePrune(self, playlistId: str, includeSoftDeleted: bool = False) -> Dict[List[Playlist], List[QueueStream]]:
        """
        Prepare a prune to permanently remove all soft-deleted entities, getting data for doPrune.
        
        Args:
            playlistId (str): ID of playlist to prune.
            includeSoftDeleted (bool, optional): Should include soft-deleted entities. Defaults to False.
            
        Returns:
            Dict[List[Playlist], List[QueueStream]]: Entities to remove.
        """
        
        data = PlaylistDetailed()

        playlist = self.playlistService.get(playlistId, includeSoftDeleted)
        if(playlist == None or playlist.playWatchedStreams):
            return PlaylistDetailed()
        
        for id in playlist.streamIds:
            stream = self.queueStreamService.get(id, includeSoftDeleted)
            if(stream != None and stream.watched != None):
                data.queueStreams.append(stream)
        
        if(len(data.queueStreams) > 0):
            data.playlists.append(playlist)
        
        return data
    
    def doPrune(self, data: Dict[List[Playlist], List[QueueStream]], includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> bool:
        """
        Prune (permanently remove/soft delete) watched QueueStreams from Playlists given as data.
        
        Args:
            Dict[List[Playlist], List[QueueStream]]): Data to remove.
            includeSoftDeleted (bool): Should soft-deleted entities be deleted.
            permanentlyDelete (bool): Should entities be permanently deleted.
            
        Returns:
            bool: Result.
        """
        
        for stream in data.queueStreams:
            if(permanentlyDelete):
                self.queueStreamService.remove(stream.id, includeSoftDeleted)
            else:
                self.queueStreamService.delete(stream.id)
                
            for playlist in data.playlists:
                playlist.streamIds.remove(stream.id)
                result = self.playlistService.update(playlist)
                if(not result):
                    printD("failed to update Playlist \"", playlist.name, "\".", color = BashColor.WARNING, debug = self.settings.debug)
                    return False
                    
        return True
    
    def preparePurge(self) -> PlaylistDetailed:
        """
        Prepare a purge to permanently remove all soft-deleted entities, getting data for doPurge.
            
        Returns:
            PlaylistDetailed: Entities to remove.
        """
        
        data = PlaylistDetailed()
        
        allQ = self.queueStreamService.getAll(includeSoftDeleted = True)
        data.queueStreams = [_ for _ in allQ if _.deleted != None]
        allS = self.streamSourceService.getAll(includeSoftDeleted = True)
        data.streamSources = [_ for _ in allS if _.deleted != None]
        allP = self.playlistService.getAll(includeSoftDeleted = True)
        data.playlists = [_ for _ in allP if _.deleted != None]
        
        return data
    
    def doPurge(self, data: PlaylistDetailed) -> bool:
        """
        Purge (permanently remove) all soft-deleted entities given as data.
            
        Args:
            data (PlaylistDetailed): Data to remove.
            
        Returns:
            bool: Result.
        """
        
        for _ in data.queueStreams:
            self.queueStreamService.remove(_.id, True)
        for _ in data.streamSources:
            self.streamSourceService.remove(_.id, True)
        for _ in data.playlists:
            self.playlistService.remove(_.id, True)
            
        return True
    
    def preparePurgePlaylists(self, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> PlaylistDetailed:
        """
        Prepare a purge to delete/permanently remove QueueStreams and StreamSources from DB, while removing IDs with no entity from Playlists, getting data for doPurgePlaylists.
        
        Args:
            includeSoftDeleted (bool): Should soft-deleted entities be deleted.
            permanentlyDelete (bool): Should entities be permanently deleted.
            
        Returns:
            PlaylistDetailed: Entities to remove.
        """
        
        data = PlaylistDetailed()
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
                data.queueStreams.append(entity)
        for id in unlinkedPlaylistStreamStreamIds:
            if(not id in allPlaylistStreamStreamIds):
                entity = self.streamSourceService.get(id, includeSoftDeleted)
                data.streamSources.append(entity)
        
        # Find IDs in Playlists with no corresponding entity
        for playlist in playlists:
            for id in playlist.streamIds:
                if(not self.queueStreamService.exists(id)):
                    data.playlists.append(playlist)
                    break
                
            for id in playlist.streamSourceIds:
                if(not self.streamSourceService.exists(id)):
                    data.playlists.append(playlist)
                    break
                
        return data
    
    def doPurgePlaylists(self, data: PlaylistDetailed) -> bool:
        """
        Purge Playlists given as data for dangling IDs.
            
        Args:
            data (PlaylistDetailed): Data to remove where Playlist-list is Playlists to update, and str-list are IDs to remove from any field in Playlists.
            
        Returns:
            bool: Result.
        """
        
        for playlist in data.playlists:
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

    def search(self, searchTerm: str, includeSoftDeleted: bool = False) -> PlaylistDetailed:
        """
        Search names and URIs for Regex-term searchTerm and returns a Dict with results.

        Args:
            searchTerm (str): Regex-enabled term to search for.
            includeSoftDeleted (bool, optional): Should include soft deleted entities. Defaults to False.

        Returns:
            PlaylistDetailed: Entities that matched the searchTerm.
        """
        
        data = PlaylistDetailed()
        
        queueStreams = self.queueStreamService.getAll(includeSoftDeleted)
        streamSources = self.streamSourceService.getAll(includeSoftDeleted)
        playlists = self.playlistService.getAll(includeSoftDeleted)
        
        for entity in queueStreams:
            if(self.searchFields(searchTerm, entity.name, entity.uri) > 0):
                data.queueStreams.append(entity)
        for entity in streamSources:
            if(self.searchFields(searchTerm, entity.name, entity.uri) > 0):
                data.streamSources.append(entity)
        for entity in playlists:
            if(self.searchFields(searchTerm, entity.name) > 0):
                data.playlists.append(entity)
        
        found = len(data.queueStreams) > 0 or len(data.streamSources) > 0 or len(data.playlists) > 0
        printS("No results", color = BashColor.WARNING, doPrint = not found)
        
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
    
    def getAllSoftDeleted(self) -> PlaylistDetailed:
        """
        Returns a Dict with Lists of all soft deleted entities.

        Returns:
            PlaylistDetailed: Entities that matched the searchTerm.
        """
        
        data = PlaylistDetailed()
        
        queueStreams = self.queueStreamService.getAll(includeSoftDeleted = True)
        streamSources = self.streamSourceService.getAll(includeSoftDeleted = True)
        playlists = self.playlistService.getAll(includeSoftDeleted = True)
        
        for entity in queueStreams:
            if(entity.deleted != None):
                data.queueStreams.append(entity)
        for entity in streamSources:
            if(entity.deleted != None):
                data.streamSources.append(entity)
        for entity in playlists:
            if(entity.deleted != None):
                data.playlists.append(entity)
        
        return data
    