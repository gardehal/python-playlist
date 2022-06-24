import os

import validators
from dotenv import load_dotenv
from grdUtil.BashColor import BashColor
from grdUtil.PrintUtil import printS
from model.QueueStream import QueueStream
from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.SharedService import SharedService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))

class QueueStreamCliController():
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    sharedService: SharedService = None

    def __init__(self):
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.sharedService = SharedService()

    def addQueueStream(self, playlistId: str, uri: str, name: str) -> list[QueueStream]:
        """
        Add QueueStreams to Playlist.
        
        Args:
            playlistId (str): ID of Playlist to add to.
            uri (str): URI of stream to add.
            name (str): Displayname of QueueStream.

        Returns:
            list[QueueStream]: QueueStreams added.
        """
     
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
    
    def deleteQueueStream(self, playlistId: str, queueStreamIds: list[str]) -> list[QueueStream]:
        """
        (Soft) Delete/remove QueueStreams from Playlist.
        
        Args:
            playlistId (str): ID of Playlist to add to.
            streamIds (list[str]): IDs of QueueStreams to remove.

        Returns:
            list[QueueStream]: QueueStream deleted/removed.
        """
        
        playlist = self.playlistService.get(playlistId)
        result = self.playlistService.deleteStreams(playlist.id, queueStreamIds)
        if(len(result) > 0):
            printS("Deleted ", len(result), " QueueStreams successfully from Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
        else:
            printS("Failed to delete QueueStreams.", color = BashColor.FAIL)
            
        return result
