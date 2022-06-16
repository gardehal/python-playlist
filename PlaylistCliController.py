import os

from dotenv import load_dotenv
from grdException.ArgumentException import ArgumentException
from grdUtil.BashColor import BashColor
from grdUtil.PrintUtil import printLists, printS
from grdUtil.StaticUtil import StaticUtil

from model.Playlist import Playlist
from model.QueueStream import QueueStream
from PlaylistService import PlaylistService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

class PlaylistCliController():
    playlistService: PlaylistService = None

    def __init__(self):
        self.playlistService = PlaylistService()
        
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