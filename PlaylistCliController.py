import os

from dotenv import load_dotenv
from grdUtil.BashColor import BashColor
from grdUtil.PrintUtil import printLists, printS

from model.Playlist import Playlist
from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService
from StreamSourceService import StreamSourceService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

class PlaylistCliController():
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None

    def __init__(self):
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.streamSourceService = StreamSourceService()
        
    def addPlaylist(self, name: str, playWatchedStreams: bool, allowDuplicates: bool, streamSourceIds: list[str]) -> Playlist:
        """
        Add a playlist to storage.

        Args:
            name (str): Name of Playlist.
            playWatchedStreams (bool): Should Playlist play watched streams when playing?
            allowDuplicates (bool): Should Playlist allow duplicate QueueStreams (URLs)?
            streamSourceIds (list[str]): List of IDs or indices to add to Playlist.

        Returns:
            Playlist: Result.
        """
        
        entity = Playlist(name = name, playWatchedStreams = playWatchedStreams, allowDuplicates = allowDuplicates, streamSourceIds = streamSourceIds)
        result = self.playlistService.add(entity)
        
        if(result != None):
            printS("Playlist \"", result.name, "\" added successfully.", color = BashColor.OKGREEN)
        else:
            printS("Failed to create Playlist.", color = BashColor.FAIL)

        return result
        
    def addYouTubePlaylist(self, url: str, name: str, playWatchedStreams: bool, allowDuplicates: bool) -> Playlist:
        """
        Add a playlist to storage.

        Args:
            url (str): URL to Youtube playlist.
            name (str): Name of Playlist.
            playWatchedStreams (bool): Should Playlist play watched streams when playing?
            allowDuplicates (bool): Should Playlist allow duplicate QueueStreams (URLs)?

        Returns:
            Playlist: Result.
        """
        
        entity = Playlist(name = name, playWatchedStreams = playWatchedStreams, allowDuplicates = allowDuplicates)
        result = self.playlistService.addYouTubePlaylist(entity, url)
        if(result != None):
            printS("Playlist \"", result.name, "\" added successfully from YouTube playlist.", color = BashColor.OKGREEN)
        else:
            printS("Failed to create Playlist.", color = BashColor.FAIL)

        return result
        
    def deletePlaylists(self, ids: list[str]) -> list[Playlist]:
        """
        Delete Playlists given by IDs.

        Args:
            ids (list[str]): List of IDs or indices to delete from storage.

        Returns:
            list[Playlist]: Playlists deleted.
        """
        
        entitiesAltered = []         
        for id in ids:
            result = self.playlistService.delete(id)
            if(result != None):
                printS("Playlist \"", result.name, "\" deleted successfully.", color = BashColor.OKGREEN)
                entitiesAltered.append(result)
            else:
                printS("Failed to delete Playlist.", color = BashColor.FAIL)

        return entitiesAltered
        
    def restorePlaylists(self, ids: list[str]) -> list[Playlist]:
        """
        Restore Playlists given by IDs.

        Args:
            ids (list[str]): List of IDs or indices to restore (must be deleted).

        Returns:
            list[Playlist]: Playlists restored.
        """
        
        entitiesAltered = []
        for id in ids:
            result = self.playlistService.restore(id)
            if(result != None):
                printS("Playlist \"", result.name, "\" restore successfully.", color = BashColor.OKGREEN)
                entitiesAltered.append(result)
            else:
                printS("Failed to restore Playlist.", color = BashColor.FAIL)

        return entitiesAltered
        
    def listPlaylists(self, includeSoftDeleted: bool) -> list[Playlist]:
        """
        List Playlist in console.

        Args:
            includeSoftDeleted (bool,): Should include soft-deleted entities?

        Returns:
            list[Playlist]: Playlists restored.
        """
        
        data = []
        result = self.playlistService.getAll(includeSoftDeleted)
        if(len(result) > 0):
            nPlaylists = len(result)
            nQueueStreams = len(self.queueStreamService.getAll(includeSoftDeleted))
            nStreamSources = len(self.streamSourceService.getAll(includeSoftDeleted))
            titles = [str(nPlaylists) + " Playlists, " + str(nQueueStreams) + " QueueStreams, " + str(nStreamSources) + " StreamSources."]
            
            for (i, entry) in enumerate(result):
                data.append(str(i) + " - " + entry.summaryString())
                
            printLists([data], titles)

        return data
    