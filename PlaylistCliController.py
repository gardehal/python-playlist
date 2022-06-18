import os
from datetime import datetime

from dotenv import load_dotenv
from grdUtil.BashColor import BashColor
from grdUtil.PrintUtil import printLists, printS

from FetchService import FetchService
from model.Playlist import Playlist
from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService
from StreamSourceService import StreamSourceService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

class PlaylistCliController():
    fetchService = FetchService()
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None

    def __init__(self):
        self.fetchService = FetchService()
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
        
    def printPlaylists(self, includeSoftDeleted: bool) -> list[Playlist]:
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
    
    def printPlaylistsDetailed(self, playlistIds: list[str], includeUri: bool, includeId: bool, includeDatetime: bool, includeListCount: bool, includeSource: bool) -> int:
        """
        Print detailed info for Playlist, including details for related StreamSources and QueueStreams.

        Args:
            playlistIds (list[str]): list of playlistIds to print details of.
            includeUri (bool, optional): should print include URI if any. Defaults to False.
            includeId (bool, optional): should print include IDs. Defaults to False.
            includeSource (bool, optional): should print include StreamSource this was fetched from. Defaults to True.
            
        Returns:
            int: number of playlists printed for.
        """
        
        result = self.playlistService.printPlaylistDetails(playlistIds, includeUri, includeId, includeDatetime, includeListCount, includeSource)
        if(result):
            printS("Finished printing ", result, " details.", color = BashColor.OKGREEN)
        else:
            printS("Failed print details.", color = BashColor.FAIL)

        return result
    
    def fetchPlaylists(self, playlistId: str, batchSize: int = 10, takeAfter: datetime = None, takeBefore: datetime = None, takeNewOnly: bool = False) -> int:
        """
        Fetch new videos from watched sources, adding them in chronological order.

        Args:
            batchSize (int): Number of videos to check at a time, unrelated to max videos that will be read.  Defaults to 10.
            takeAfter (datetime): Limit to take video after.  Defaults to None.
            takeBefore (datetime): Limit to take video before.  Defaults to None.
            takeNewOnly (bool): Only take streams marked as new. Disables takeAfter and takeBefore-checks. To use takeAfter and/or takeBefore, set this to False.  Defaults to False.

        Returns:
            int: Number of videos added.
        """
        
        result = 0
        for id in playlistId:
            result += self.fetchService.fetch(id, batchSize, takeAfter, takeBefore, takeNewOnly)
            playlist = self.playlistService.get(id)
            printS("Fetched ", result, " for playlist \"", playlist.name, "\" successfully.", color = BashColor.OKGREEN)
    
        return result
