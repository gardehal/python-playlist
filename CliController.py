import os

from dotenv import load_dotenv
from grdUtil.BashColor import BashColor
from grdUtil.PrintUtil import printLists, printS
from grdUtil.StaticUtil import StaticUtil

from FetchService import FetchService
from LegacyService import LegacyService
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource
from PlaybackService import PlaybackService
from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService
from SharedService import SharedService
from StreamSourceService import StreamSourceService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")
FETCH_LIMIT_SINGLE_SOURCE = int(os.environ.get("FETCH_LIMIT_SINGLE_SOURCE"))

class SharedCliController():
    fetchService: FetchService = None
    legacyService: LegacyService = None
    playbackService: PlaybackService = None
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    sharedService: SharedService = None
    streamSourceService: StreamSourceService = None

    def __init__(self):
        self.fetchService = FetchService()
        self.legacyService = LegacyService()
        self.playbackService = PlaybackService()
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.sharedService = SharedService()
        self.streamSourceService = StreamSourceService()
        
    def prune(self, id: str, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> dict[list[Playlist], list[QueueStream]]:
        """
        Removes watched streams from a Playlist if it does not allow replaying of already played streams (playWatchedStreams == False).

        Args:
            id (str): ID of Playlists to prune.
            includeSoftDeleted (bool, optional): Should include soft-deleted entities. Defaults to False.
            permanentlyDelete (bool, optional): Should entities be permanently deleted. Defaults to False.

        Returns:
            dict[list[QueueStream], list[str]]: Result.
        """
        
        if(id == None):
            printS("Missing input: playlistId or index.", color = BashColor.FAIL)
            return None
        
        data = self.sharedService.preparePrune(id, includeSoftDeleted)
        if(not data["QueueStream"] and not data["Playlist"]):
            printS("Prune aborted, nothing to prune.", color = BashColor.OKGREEN)
            return None
        
        pTitle = "Playlist"
        pDataList = [(_.id + " - " + _.name) for _ in data["Playlist"]]
        qTitle = "QueueStream(s)"
        qDataList = [(_.id + " - " + _.name) for _ in data["QueueStream"]]
        
        printLists([pDataList, qDataList], [pTitle, qTitle])
        printS("\nDo you want to ", ("PERMANENTLY REMOVE" if permanentlyDelete else "DELETE"), " this data?", color = BashColor.WARNING)
        inputArgs = input("(y/n): ")
        
        if(inputArgs not in StaticUtil.affirmative):
            printS("Prune aborted by user.", color = BashColor.WARNING)
            return None
        else:
            result = self.sharedService.doPrune(data, includeSoftDeleted, permanentlyDelete)
            if(result):
                printS("Prune completed.", color = BashColor.OKGREEN)
            else:
                printS("Prune failed.", color = BashColor.FAIL)
        
        return data
    
    def purgePlaylists(self, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> dict[list[QueueStream], list[StreamSource], list[Playlist]]:
        """
        Purges deleted entities.

        Args:
            includeSoftDeleted (bool, optional): Should include soft-deleted entities. Defaults to False.
            permanentlyDelete (bool, optional): Should entities be permanently deleted. Defaults to False.
            
        Returns:
            dict[list[QueueStream], list[StreamSource], list[Playlist]]: dict with lists of entities removed.
        """
        
        data = self.sharedService.preparePurgePlaylists(includeSoftDeleted, permanentlyDelete)
        if(not data["QueueStream"] and not data["StreamSource"] and not data["Playlist"]):
            printS("Purge aborted, nothing to purge.", color = BashColor.OKGREEN)
            return None
        
        qTitle = "QueueStream(s)"
        qDataList = [(_.id + " - " + _.name) for _ in data["QueueStream"]]
        sTitle = "StreamSource(s)"
        sDataList = [(_.id + " - " + _.name) for _ in data["StreamSource"]]
        pTitle = "Playlist(s) updated"
        pDataList = [(_.id + " - " + _.name) for _ in data["Playlist"]]
        
        printLists([qDataList, sDataList, pDataList], [qTitle, sTitle, pTitle])
        printS("\nDo you want to ", ("PERMANENTLY REMOVE" if permanentlyDelete else "DELETE"), " this data?", color = BashColor.WARNING)
        inputArgs = input("(y/n): ")
        
        if(inputArgs not in StaticUtil.affirmative):
            printS("Purge aborted by user.", color = BashColor.WARNING)
            return None
        else:
            # Remove Playlists from purged data, will only be updated
            entitiesToRemove = data.copy()
            entitiesToRemove["Playlist"] = []
            result = self.sharedService.doPurge(entitiesToRemove)
            result = result and self.sharedService.doPurgePlaylists(data)
            if(result):
                printS("Purge completed.", color = BashColor.OKGREEN)
            else:
                printS("Purge failed.", color = BashColor.FAIL)
             
        return data
    
    def purge(self) -> dict[list[QueueStream], list[StreamSource], list[Playlist]]:
        """
        Purges deleted entities.
            
        Returns:
            dict[list[QueueStream], list[StreamSource], list[Playlist]]: dict with lists of entities removed.
        """
        
        data = self.sharedService.preparePurge()
        if(not data["QueueStream"] and not data["StreamSource"] and not data["Playlist"]):
            printS("Purge aborted, nothing to purge.", color = BashColor.OKGREEN)
            return None
        
        qTitle = "QueueStream(s)"
        qDataList = [(_.id + " - " + _.name) for _ in data["QueueStream"]]
        sTitle = "StreamSource(s)"
        sDataList = [(_.id + " - " + _.name) for _ in data["StreamSource"]]
        pTitle = "Playlist(s)"
        pDataList = [(_.id + " - " + _.name) for _ in data["Playlist"]]
        
        printLists([qDataList, sDataList, pDataList], [qTitle, sTitle, pTitle])
        printS("\nDo you want to PERMANENTLY REMOVE this data?", color = BashColor.WARNING)
        inputArgs = input("(y/n): ")
        
        if(inputArgs not in StaticUtil.affirmative):
            printS("Purge aborted by user.", color = BashColor.WARNING)
            return None
        else:
            result = self.sharedService.doPurge(data)
            if(result):
                printS("Purge completed.", color = BashColor.OKGREEN)
            else:
                printS("Purge failed.", color = BashColor.FAIL)
        
        return data
    