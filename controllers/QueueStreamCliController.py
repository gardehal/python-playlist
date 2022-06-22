import os

from dotenv import load_dotenv
from grdUtil.BashColor import BashColor
from grdUtil.PrintUtil import printS
from model.QueueStream import QueueStream
from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))

class QueueStreamCliController():
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None

    def __init__(self):
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()

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
        
        playlist = self.playlistService.get(playlistId)
        entity = QueueStream(name = name, uri = uri)
        result = self.playlistService.addStreams(playlist.id, [entity])
        if(len(result) > 0):
            printS("Added QueueStream \"", result[0].name, "\" to Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
        else:
            printS("Failed to create QueueStream.", color = BashColor.FAIL)
            
        return result
    
    def deleteQueueStream(self, playlistId: str, uri: str, name: str) -> list[QueueStream]:
        """
        Add QueueStreams to Playlist.
        
        Args:
            playlistId (str): ID of Playlist to add to.
            uri (str): URI of stream to add.
            name (str): Displayname of QueueStream.

        Returns:
            list[QueueStream]: QueueStreams added.
        """
        
        playlist = self.playlistService.get(playlistId)
        result = self.playlistService.deleteStreams(playlist.id, queueStreamIds)
        if(len(result) > 0):
            printS("Deleted ", len(result), " QueueStreams successfully from Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
        else:
            printS("Failed to delete QueueStreams.", color = BashColor.FAIL)
            
        return result
