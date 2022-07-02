import os

from dotenv import load_dotenv
from grdUtil.BashColor import BashColor
from grdUtil.InputUtil import getIdsFromInput
from grdUtil.PrintUtil import printS
from Settings import Settings
from model.StreamSource import StreamSource
from services.PlaylistService import PlaylistService
from services.SharedService import SharedService
from services.StreamSourceService import StreamSourceService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

class StreamSourceCliController():
    playlistService: PlaylistService = None
    sharedService: SharedService = None
    streamSourceService: StreamSourceService = None
    settings: Settings = None

    def __init__(self):
        self.playlistService = PlaylistService()
        self.sharedService = SharedService()
        self.streamSourceService = StreamSourceService()
        self.settings = Settings()
    
    def addStreamSource(self, playlistId: str, uri: str, enableFetch: bool, backgroundContent: bool, name: str) -> list[StreamSource]:
        """
        Add a StreamSource to Playlist.
        
        Args:
            playlistId (str): ID of Playlist to add to.
            uri (str): URI of source to add.
            enableFetch (bool): Should streams be fetched from this source?
            backgroundContent (bool): Is the contents this source provides background content (not something to actively pay attention to)?
            name (str): Displayname of StreamSource.

        Returns:
            list[StreamSource]: StreamSources added.
        """
        
        if(len(playlistId) == 0):
            printS("Failed to add StreamSource, missing playlistId or index.", color = BashColor.FAIL)
            return []

        if(uri == None):
            printS("Failed to add StreamSource, missing uri.", color = BashColor.FAIL)
            return []
        
        if(name == None):
            name = self.sharedService.getPageTitle(uri)
            if(name == None):
                name = "NewStreamSource"
                printS("Could not automatically get the web name for this StreamSource, will be named \"" , name, "\".", color = BashColor.WARNING)                  
            
        playlist = self.playlistService.get(playlistId)
        entity = StreamSource(name = name, uri = uri, enableFetch = enableFetch, backgroundContent = backgroundContent)
        result = self.playlistService.addStreamSources(playlist.id, [entity])
        if(len(result) > 0):
            printS("Added StreamSource \"", result[0].name, "\" to Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
        else:
            printS("Failed to create StreamSource.", color = BashColor.FAIL)
            
        return result
    
    def deleteStreamSources(self, playlistId: str, streamSourceIds: list[str]) -> list[StreamSource]:
        """
        (Soft) Delete StreamSources from Playlist.
        
        Args:
            playlistId (str): ID of Playlist to delete from.
            streamSourceIds (list[str]): IDs of StreamSources to delete.

        Returns:
            list[StreamSource]: StreamSources deleted.
        """
        
        if(playlistId == None):
            printS("Failed to delete StreamSources, missing playlistId or index.", color = BashColor.FAIL)
            return []
        
        playlist = self.playlistService.get(playlistId)
        streamSourceIds = getIdsFromInput(streamSourceIds, playlist.streamSourceIds, self.playlistService.getSourcesByPlaylistId(playlist.id), debug = self.settings.debug)
        if(len(streamSourceIds) == 0):
            printS("Failed to delete StreamSources, missing streamSourceIds or indices.", color = BashColor.FAIL)
            return []
        
        result = self.playlistService.deleteStreamSources(playlist.id, streamSourceIds)
        if(len(result) > 0):
            printS("Deleted ", len(result), " StreamSources successfully from playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
        else:
            printS("Failed to delete StreamSources.", color = BashColor.FAIL)
            
        return result
       
    def restoreStreamSources(self, playlistId: str, streamSourceIds: list[str]) -> list[StreamSource]:
        """
        Restore StreamSources to Playlist.
        
        Args:
            playlistId (str): ID of Playlist to restore to.
            streamSourceIds (list[str]): IDs of StreamSources to restore.

        Returns:
            list[StreamSource]: StreamSources restored.
        """
        
        if(playlistId == None):
            printS("Failed to restore StreamSources, missing playlistId or index.", color = BashColor.FAIL)
            return []
        
        playlist = self.playlistService.get(playlistId)
        streamSourceIds = getIdsFromInput(streamSourceIds, self.streamSourceService.getAllIds(includeSoftDeleted = True), self.playlistService.getSourcesByPlaylistId(playlist.id, includeSoftDeleted = True), debug = self.settings.debug)
        if(len(streamSourceIds) == 0):
            printS("Failed to restore StreamSources, missing streamSourceIds or indices.", color = BashColor.FAIL)
            return []
        
        result = self.playlistService.restoreStreamSources(playlist.id, streamSourceIds)
        if(len(result) > 0):
            printS("Restored ", len(result), " StreamSources successfully from Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
        else:
            printS("Failed to restore StreamSources.", color = BashColor.FAIL)
            
        return result
