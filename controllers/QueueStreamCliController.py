from typing import List

import validators
from grdUtil.BashColor import BashColor
from grdUtil.InputUtil import getIdsFromInput
from grdUtil.PrintUtil import printS
from model.QueueStream import QueueStream
from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.SharedService import SharedService
from Settings import Settings


class QueueStreamCliController():
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    sharedService: SharedService = None
    settings: Settings = None

    def __init__(self):
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.sharedService = SharedService()
        self.settings = Settings()

    def addQueueStream(self, playlistId: str, uri: str, name: str) -> List[QueueStream]:
        """
        Add QueueStreams to Playlist.
        
        Args:
            playlistId (str): ID of Playlist to add to.
            uri (str): URI of stream to add.
            name (str): Displayname of QueueStream.

        Returns:
            List[QueueStream]: QueueStreams added.
        """

        if(playlistId == None):
            printS("Failed to add QueueStream, missing playlistId or index.", color = BashColor.FAIL)
            return []

        if(uri == None):
            printS("Failed to add QueueStream, missing uri.", color = BashColor.FAIL)
            return []
        
        if(name == None and validators.url(uri)):
            name = self.sharedService.getPageTitle(uri)
            if(name == None):
                printS("Could not automatically get the web name for this QueueStream, try setting it manually.", color = BashColor.FAIL)
                return []
            
        playlist = self.playlistService.get(playlistId)   
        entity = QueueStream(name = name, uri = uri)
        result = self.playlistService.addStreams(playlist.id, [entity])
        if(len(result) > 0):
            printS("Added QueueStream \"", result[0].name, "\" to Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
        else:
            printS("Failed to create QueueStream.", color = BashColor.FAIL)
            
        return result

    def addQueueStreams(self, playlistId: str, uris: List[str]) -> List[QueueStream]:
        """
        Add multiple QueueStreams to Playlist.
        
        Args:
            playlistId (str): ID of Playlist to add to.
            uris (List[str]): URIs of streams to add.

        Returns:
            List[QueueStream]: QueueStreams added.
        """

        if(playlistId == None):
            printS("Failed to add QueueStreams, missing playlistId or index.", color = BashColor.FAIL)
            return []

        if(uris == None or len(uris) < 1):
            printS("Failed to add QueueStreams, missing uri(s).", color = BashColor.FAIL)
            return []
            
        result = []
        for uri in uris:
            added = self.addQueueStream(playlistId, uri, None)
            result.append(*added)
            
        return result
    
    def deleteQueueStreams(self, playlistId: str, queueStreamIds: List[str]) -> List[QueueStream]:
        """
        (Soft) Delete QueueStreams from Playlist.
        
        Args:
            playlistId (str): ID of Playlist to delete from.
            queueStreamIds (list[str]): IDs of QueueStreams to delete.

        Returns:
            List[QueueStream]: QueueStreams deleted.
        """
        
        if(playlistId == None):
            printS("Failed to delete QueueStreams, missing playlistId or index.", color = BashColor.FAIL)
            return []
        
        playlist = self.playlistService.get(playlistId)
        queueStreamIds = getIdsFromInput(queueStreamIds, playlist.streamIds, self.playlistService.getStreamsByPlaylistId(playlistId), startAtZero = False, debug = self.settings.debug)
        if(len(queueStreamIds) == 0):
            printS("Failed to delete QueueStreams, missing queueStreamIds or indices.", color = BashColor.FAIL)
            return []
        
        result = self.playlistService.deleteStreams(playlist.id, queueStreamIds)
        if(len(result) > 0):
            printS("Deleted ", len(result), " QueueStreams successfully from Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
        else:
            printS("Failed to delete QueueStreams.", color = BashColor.FAIL)
            
        return result
    
    def restoreQueueStreams(self, playlistId: str, queueStreamIds: List[str]) -> List[QueueStream]:
        """
        Restore QueueStreams to Playlist.
        
        Args:
            playlistId (str): ID of Playlist to restore to.
            queueStreamIds (list[str]): IDs of QueueStreams to restore.

        Returns:
            List[QueueStream]: QueueStreams restored.
        """
        
        if(playlistId == None):
            printS("Failed to restore QueueStreams, missing playlistId or index.", color = BashColor.FAIL)
            return []
        
        playlist = self.playlistService.get(playlistId)
        queueStreamIds = getIdsFromInput(queueStreamIds, self.queueStreamService.getAllIds(includeSoftDeleted = True), self.playlistService.getStreamsByPlaylistId(playlist.id, includeSoftDeleted = True), setDefaultId = False, startAtZero = False, debug = self.settings.debug)
        if(len(queueStreamIds) == 0):
            printS("Failed to restore QueueStreams, missing queueStreamIds or indices.", color = BashColor.FAIL)
            return []
        
        playlist = self.playlistService.get(playlistId)
        result = self.playlistService.restoreStreams(playlist.id, queueStreamIds)
        if(len(result) > 0):
            printS("Restored ", len(result), " QueueStreams successfully from Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
        else:
            printS("Failed to restore QueueStreams.", color = BashColor.FAIL)
            
        return result
