from datetime import datetime
from typing import List

from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTime, stringToDatetime
from grdUtil.InputUtil import isNumber
from grdUtil.PrintUtil import printLists, printS
from model.Playlist import Playlist
from services.FetchService import FetchService
from services.PlaybackService import PlaybackService
from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.StreamSourceService import StreamSourceService
from Settings import Settings

from controllers.SharedCliController import SharedCliController


class PlaylistCliController():
    settings: Settings = None
    fetchService: FetchService() = None
    playbackService: PlaybackService = None
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    sharedCliController: SharedCliController = None

    def __init__(self):
        self.settings = Settings()
        self.fetchService = FetchService()
        self.playbackService = PlaybackService()
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.streamSourceService = StreamSourceService()
        self.sharedCliController = SharedCliController()
        
    def addPlaylist(self, name: str, playWatchedStreams: bool, allowDuplicates: bool, streamSourceIds: List[str]) -> Playlist:
        """
        Add a playlist to storage.

        Args:
            name (str): Name of Playlist.
            playWatchedStreams (bool): Should Playlist play watched streams when playing?
            allowDuplicates (bool): Should Playlist allow duplicate QueueStreams (URLs)?
            streamSourceIds (list[str]): List of IDs or indices to add to Playlist.

        Returns:
            Playlist: Playlist added.
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
            Playlist: Playlist added.
        """
        
        entity = Playlist(name = name, playWatchedStreams = playWatchedStreams, allowDuplicates = allowDuplicates)
        result = self.playlistService.addYouTubePlaylist(entity, url)
        if(result != None):
            printS("Playlist \"", result.name, "\" added successfully from YouTube playlist.", color = BashColor.OKGREEN)
        else:
            printS("Failed to create Playlist.", color = BashColor.FAIL)

        return result
        
    def deletePlaylists(self, playlistIds: List[str]) -> List[Playlist]:
        """
        Delete Playlists given by IDs.

        Args:
            playlistIds (list[str]): List of IDs or indices to delete from storage.

        Returns:
            List[Playlist]: Playlists deleted.
        """
        
        result = []
        
        if(len(playlistIds) == 0):
            printS("Failed to delete Playlists, missing playlistIds or indices.", color = BashColor.FAIL)
            return result
              
        for id in playlistIds:
            deleteResult = self.playlistService.delete(id)
            if(deleteResult != None):
                printS("Playlist \"", deleteResult.name, "\" deleted successfully.", color = BashColor.OKGREEN)
                result.append(deleteResult)
            else:
                printS("Failed to delete Playlist.", color = BashColor.FAIL)

        return result
        
    def restorePlaylists(self, playlistIds: List[str]) -> List[Playlist]:
        """
        Restore Playlists given by IDs.

        Args:
            playlistIds (list[str]): List of IDs or indices to restore (must be deleted but not removed).

        Returns:
            List[Playlist]: Playlists restored.
        """

        result = []
        
        if(len(playlistIds) == 0):
            printS("Failed to restore Playlists, missing playlistIds or indices.", color = BashColor.FAIL)
            return result
                    
        for id in playlistIds:
            restoreResult = self.playlistService.restore(id)
            if(restoreResult != None):
                printS("Playlist \"", restoreResult.name, "\" restored successfully.", color = BashColor.OKGREEN)
                result.append(restoreResult)
            else:
                printS("Failed to restore Playlist.", color = BashColor.FAIL)

        return result
        
    def printPlaylists(self, includeSoftDeleted: bool) -> List[Playlist]:
        """
        List Playlist in console.

        Args:
            includeSoftDeleted (bool,): Should include soft-deleted entities?

        Returns:
            List[Playlist]: Playlists restored.
        """
        
        result = []
        all = self.playlistService.getAll(includeSoftDeleted)
        if(len(all) > 0):
            nPlaylists = len(all)
            nQueueStreams = len(self.queueStreamService.getAll(includeSoftDeleted))
            nStreamSources = len(self.streamSourceService.getAll(includeSoftDeleted))
            titles = [str(nPlaylists) + " Playlists, " + str(nQueueStreams) + " QueueStreams, " + str(nStreamSources) + " StreamSources."]
            
            for (i, entry) in enumerate(all):
                result.append(str(i) + " - " + entry.summaryString())
                
            printLists([result], titles)
        else:
            printS("No Playlists found.")

        return result
    
    def printPlaylistsDetailed(self, playlistIds: List[str], includeUri: bool, includeId: bool, includeDatetime: bool, includeListCount: bool, includeSource: bool) -> int:
        """
        Print detailed info for Playlist, including details for related StreamSources and QueueStreams.

        Args:
            playlistIds (list[str]): List of playlistIds to print details of.
            includeUri (bool, optional): should print include URI if any. Defaults to False.
            includeId (bool, optional): should print include IDs. Defaults to False.
            includeSource (bool, optional): should print include StreamSource this was fetched from. Defaults to True.
            
        Returns:
            int: number of playlists printed for.
        """
            
        result = 0
        if(len(playlistIds) == 0):
            printS("Failed to print details, missing playlistIds or indices.", color = BashColor.FAIL)
            return result
        
        result = self.playlistService.printPlaylistDetails(playlistIds, includeUri, includeId, includeDatetime, includeListCount, includeSource)
        if(result):
            printS("Finished printing ", result, " details.", color = BashColor.OKGREEN)
        else:
            printS("Failed print details.", color = BashColor.FAIL)

        return result
    
    def printWatchedStreams(self, playlistIds: List[str]) -> int:
        """
        Print watched QueueStreams in playlists given by IDs.

        Args:
            playlistIds (list[str]): List of playlistIds to print details of.
            
        Returns:
            int: number of streams watched.
        """
            
        result = 0
        if(len(playlistIds) == 0):
            printS("Failed to print watched streams, missing playlistIds or indices.", color = BashColor.FAIL)
            return result
        
        result = self.playlistService.printWatchedStreams(playlistIds)
        if(result):
            printS("Finished printing ", result, " details.", color = BashColor.OKGREEN)
        else:
            printS("Failed print details.", color = BashColor.FAIL)

        return result
    
    def fetchPlaylists(self, playlistIds: List[str], batchSize: int, takeAfter: datetime, takeBefore: datetime, takeNewOnly: bool) -> int:
        """
        Fetch new videos from watched sources, adding them in chronological order.

        Args:
            playlistIds (list[str]): IDs of Playlists to fetch for.
            batchSize (int): Number of videos to check at a time, unrelated to max videos that will be read. 
            takeAfter (datetime): Limit to take video after.
            takeBefore (datetime): Limit to take video before.
            takeNewOnly (bool): Only take streams marked as new. Disables takeAfter and takeBefore-checks. To use takeAfter and/or takeBefore, set this to False.

        Returns:
            int: Number of videos added.
        """

        result = 0
        _takeAfter = None
        _takeBefore = None
        
        try:
            if(takeAfter != None):
                _takeAfter = datetime.strptime(takeAfter, "%Y-%m-%d")
            if(takeBefore != None):
                _takeBefore = datetime.strptime(takeBefore, "%Y-%m-%d")
        except:
            printS("Dates for takeAfter or takeBefore were not valid, see help print for format.", color = BashColor.FAIL)
            return result
        
        if(len(playlistIds) == 0):
            printS("Failed to fetch, missing playlistIds or indices.", color = BashColor.FAIL)
            return result
        
        started = getDateTime()
        for id in playlistIds:
            if(self.settings.removeWatchedOnFetch):
                self.sharedCliController.prune(id)
                print("") # Space before fetching
            
            result += self.fetchService.fetch(id, batchSize, _takeAfter, _takeBefore, takeNewOnly)
            playlist = self.playlistService.get(id)
            completed = getDateTime()
            duration = completed - started
            printS(f"Fetched {result} for playlist \"{playlist.name}\" successfully in {duration}.", color = BashColor.OKGREEN)
    
        return result
      
    def resetPlaylists(self, playlistIds: List[str]) -> int:
        """
        Fetch new videos from watched sources, adding them in chronological order.

        Args:
            playlistIds (list[str]): IDs of Playlists to fetch for.

        Returns:
            int: Number of Playlists reset.
        """
        
        result = 0
        if(len(playlistIds) == 0):
            printS("Failed to reset fetch-status of playlists, missing playlistIds or indices.", color = BashColor.FAIL)
            return result
        
        result = self.fetchService.resetPlaylistFetch(playlistIds)
        for id in playlistIds:
            playlist = self.playlistService.get(id)
            printS("Finished resetting fetch statuses for sources in Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN, doPrint = (result > 0))
            printS("Failed to reset fetch statuses for sources in Playlist \"", playlist.name, "\".", color = BashColor.FAIL, doPrint = (result == 0))
    
        return result
      
    def playPlaylists(self, playlistId: str, startIndex: int, shuffle: bool, repeat: bool) -> int:
        """
        Start playing streams from this playlist.

        Args:
            playlistId (str): ID of playlist to play from.
            startIndex (int): Index to start playing from.
            shuffle (bool): Shuffle videos.
            repeatPlaylist (bool): repeat playlist once it reaches the end.

        Returns:
            bool: Finished successfully.
        """
        
        result = False
        if(playlistId == None):
            printS("Failed to play playlist, missing playlistIds or indices.", color = BashColor.FAIL)
            return result
        
        if(not isNumber(startIndex, intOnly = True)):
            printS("Failed to play playlist, input startIndex must be an integer.", color = BashColor.FAIL)
            return result
        
        result = self.playbackService.play(playlistId, startIndex, shuffle, repeat)
        if(not result):
            playlist = self.playlistService.get(playlistId)
            printS("Failed to play Playlist \"", playlist.name, "\".", color = BashColor.FAIL)
    
        return result
