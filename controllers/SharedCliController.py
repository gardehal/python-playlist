from typing import Dict, List

from grdException.ArgumentException import ArgumentException
from grdUtil.BashColor import BashColor
from grdUtil.PrintUtil import printD, printLists, printS
from grdUtil.StaticUtil import StaticUtil
from model.Playlist import Playlist
from model.PlaylistDetailed import PlaylistDetailed
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource
from services.FetchService import FetchService
from services.LegacyService import LegacyService
from services.PlaybackService import PlaybackService
from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.SharedService import SharedService
from services.StreamSourceService import StreamSourceService
from Settings import Settings
import copy


class SharedCliController():
    settings: Settings = None
    fetchService: FetchService = None
    legacyService: LegacyService = None
    playbackService: PlaybackService = None
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    sharedService: SharedService = None
    streamSourceService: StreamSourceService = None

    def __init__(self):
        self.settings = Settings()
        self.fetchService = FetchService()
        self.legacyService = LegacyService()
        self.playbackService = PlaybackService()
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.sharedService = SharedService()
        self.streamSourceService = StreamSourceService()
        
    def prune(self, playlistId: str, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> Dict[List[Playlist], List[QueueStream]]:
        """
        Removes watched streams from a Playlist if it does not allow replaying of already played streams (playWatchedStreams == False).

        Args:
            playlistId (str): ID of Playlist to prune.
            includeSoftDeleted (bool, optional): Should include soft-deleted entities. Defaults to False.
            permanentlyDelete (bool, optional): Should entities be permanently deleted. Defaults to False.

        Returns:
            Dict[List[QueueStream], List[str]]: Result.
        """
        
        if(playlistId == None):
            raise ArgumentException(f"prune - Missing input: playlistId.")
        
        data = self.sharedService.preparePrune(playlistId, includeSoftDeleted)
        if(not data.queueStreams and not data.playlists):
            printS("Prune aborted, nothing to prune.", color = BashColor.OKGREEN)
            return None
        
        pTitle = f"Playlist"
        pDataList = [(_.id + " - " + _.name) for _ in data.playlists]
        qTitle = f"QueueStream(s) - {len(data.queueStreams)}"
        qDataList = [(_.id + " - " + _.name) for _ in data.queueStreams]
        
        printLists([pDataList, qDataList], [pTitle, qTitle])
        printS("\nDo you want to ", ("PERMANENTLY REMOVE" if permanentlyDelete else "DELETE"), " this data?", color = BashColor.WARNING)
        inputArgs = input("(y/n): ")
        
        if(inputArgs not in StaticUtil.affirmative):
            printS("Prune aborted by user.", color = BashColor.OKGREEN)
            return None
        else:
            result = self.sharedService.doPrune(data, includeSoftDeleted, permanentlyDelete)
            if(result):
                printS("Prune completed.", color = BashColor.OKGREEN)
            else:
                printS("Prune failed.", color = BashColor.FAIL)
        
        return data
    
    def purgePlaylists(self, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> PlaylistDetailed:
        """
        Purges deleted entities.

        Args:
            includeSoftDeleted (bool, optional): Should include soft-deleted entities. Defaults to False.
            permanentlyDelete (bool, optional): Should entities be permanently deleted. Defaults to False.
            
        Returns:
            PlaylistDetailed: Dict with Lists of entities removed.
        """
        
        data = self.sharedService.preparePurgePlaylists(includeSoftDeleted, permanentlyDelete)
        if(not data.queueStreams and not data.streamSources and not data.playlists):
            printS("Purge aborted, nothing to purge.", color = BashColor.OKGREEN)
            return None
        
        qTitle = f"QueueStream(s) - {len(data.queueStreams)}"
        qDataList = [(_.id + " - " + _.name) for _ in data.queueStreams]
        sTitle = f"StreamSource(s) - {len(data.streamSources)}"
        sDataList = [(_.id + " - " + _.name) for _ in data.streamSources]
        pTitle = f"Playlist(s) updated - {len(data.playlists)}"
        pDataList = [(_.id + " - " + _.name) for _ in data.playlists]
        
        printLists([qDataList, sDataList, pDataList], [qTitle, sTitle, pTitle])
        printS("\nDo you want to ", ("PERMANENTLY REMOVE" if permanentlyDelete else "DELETE"), " this data?", color = BashColor.WARNING)
        inputArgs = input("(y/n): ")
        
        if(inputArgs not in StaticUtil.affirmative):
            printS("Purge aborted by user.", color = BashColor.OKGREEN)
            return None
        else:
            # Remove Playlists from purged data, will only be updated
            entitiesToRemove = copy.copy(data)
            entitiesToRemove.playlists = []
            result = self.sharedService.doPurge(entitiesToRemove)
            result = result and self.sharedService.doPurgePlaylists(data)
            if(result):
                printS("Purge completed.", color = BashColor.OKGREEN)
            else:
                printS("Purge failed.", color = BashColor.FAIL)
             
        return data
    
    def purge(self) -> PlaylistDetailed:
        """
        Purges deleted entities.
            
        Returns:
            PlaylistDetailed: Dict with Lists of entities removed.
        """
        
        data = self.sharedService.preparePurge()
        if(not data.queueStreams and not data.streamSources and not data.playlists):
            printS("Purge aborted, nothing to purge.", color = BashColor.OKGREEN)
            return None
        
        qTitle = f"QueueStream(s) - {len(data.queueStreams)}"
        qDataList = [(_.id + " - " + _.name) for _ in data.queueStreams]
        sTitle = f"StreamSource(s) - {len(data.streamSources)}"
        sDataList = [(_.id + " - " + _.name) for _ in data.streamSources]
        pTitle = f"Playlist(s) - {len(data.playlists)}"
        pDataList = [(_.id + " - " + _.name) for _ in data.playlists]
        
        printLists([qDataList, sDataList, pDataList], [qTitle, sTitle, pTitle])
        printS("\nDo you want to PERMANENTLY REMOVE this data?", color = BashColor.WARNING)
        inputArgs = input("(y/n): ")
        
        if(inputArgs not in StaticUtil.affirmative):
            printS("Purge aborted by user.", color = BashColor.OKGREEN)
            return None
        else:
            result = self.sharedService.doPurge(data)
            if(result):
                printS("Purge completed.", color = BashColor.OKGREEN)
            else:
                printS("Purge failed.", color = BashColor.FAIL)
        
        return data
    
    def reset(self, playlistId: str, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> Playlist:
        """
        Reset the fetch-status for StreamSources of Playlist given by playlistId and deletes all QueueStreams in it.

        Args:
            playlistId (str): ID of Playlist to reset.
            includeSoftDeleted (bool, optional): Should include soft-deleted entities. Defaults to False.
            permanentlyDelete (bool, optional): Should entities be permanently deleted. Defaults to False.
            
        Returns:
            Playlist: Result.
        """
        
        if(playlistId == None):
            printD("Missing input: playlistId", color = BashColor.WARNING, debug = self.settings.debug)
            return None
        
        data = self.fetchService.prepareReset(playlistId, includeSoftDeleted)
        if(not data.playlists or (not data.queueStreams and not data.streamSources)):
            printS("Reset aborted, nothing to reset.", color = BashColor.OKGREEN)
            return None
        
        qTitle = f"QueueStream(s) - {len(data.queueStreams)}"
        qDataList = [(_.id + " - " + _.name) for _ in data.queueStreams]
        sTitle = f"StreamSource(s) - {len(data.streamSources)}"
        sDataList = [(_.id + " - " + _.name) for _ in data.streamSources]
        pTitle = f"Playlist(s) updated - {len(data.playlists)}"
        pDataList = [(_.id + " - " + _.name) for _ in data.playlists]
        
        printLists([qDataList, sDataList, pDataList], [qTitle, sTitle, pTitle])
        printS("\nDo you want to ", ("PERMANENTLY REMOVE" if permanentlyDelete else "DELETE"), " this data?", color = BashColor.WARNING)
        inputArgs = input("(y/n): ")
        
        if(inputArgs not in StaticUtil.affirmative):
            printS("Reset aborted by user.", color = BashColor.OKGREEN)
            return None
        else:
            result = self.fetchService.doReset(data, includeSoftDeleted, permanentlyDelete)
            if(result):
                printS("Reset completed.", color = BashColor.OKGREEN)
            else:
                printS("Reset failed.", color = BashColor.FAIL)
        
        return data
    