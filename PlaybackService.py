import os
import random
import subprocess
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from myutil.Util import *

from QueueStreamService import QueueStreamService
from PlaylistService import PlaylistService
from StreamSourceService import StreamSourceService
from Utility import Utility
from exception.ExceptBreak import ExceptBreak
from exception.ExceptContinue import ExceptContinue
from model.Playlist import Playlist
from model.QueueStream import QueueStream

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")
LOG_WATCHED = eval(os.environ.get("LOG_WATCHED"))
DOWNLOAD_WEB_STREAMS = eval(os.environ.get("DOWNLOAD_WEB_STREAMS"))
REMOVE_WATCHED_ON_FETCH = eval(os.environ.get("REMOVE_WATCHED_ON_FETCH"))
PLAYED_ALWAYS_WATCHED = eval(os.environ.get("PLAYED_ALWAYS_WATCHED"))
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")
BROWSER_BIN = os.environ.get("BROWSER_BIN")

class PlaybackService():
    debug: bool = DEBUG
    storagePath: str = LOCAL_STORAGE_PATH
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    utility: Utility = None
    quitInputs: List[str] = None
    skipInputs: List[str] = None
    addToInputs: List[str] = None

    def __init__(self, quitInputs: List[str] = ["quit"], skipInputs: List[str] = ["skip"], addToInputs: List[str] = ["addto"]):
        self.playlistService: PlaylistService = PlaylistService()
        self.queueStreamService: QueueStreamService = QueueStreamService()
        self.streamSourceService: StreamSourceService = StreamSourceService()
        self.utility: Utility = Utility()
        self.quitInputs: List[str] = quitInputs
        self.skipInputs: List[str] = skipInputs
        self.addToInputs: List[str] = addToInputs       

    def play(self, playlistId: str, startIndex: int = 0, shuffle: bool = False, repeatPlaylist: bool = False) -> bool:
        """
        Start playing streams from this playlist.

        Args:
            playlistId (str): ID of playlist to play from
            quitSymbols (List[str]): input from user which should end the playback. Defaults to ["quit"]
            startIndex (int): index to start playing from
            shuffle (bool): shuffle videos
            repeatPlaylist (bool): repeat playlist once it reaches the end

        Returns:
            bool: finished = True
        """

        _playlist = self.playlistService.get(playlistId)
        if(_playlist == None):
            return False

        if(len(_playlist.streamIds) == 0):
            printS("No streams found in playlist \"", _playlist.name, "\". Ending playback.")
            return False

        _streams = []
        _rawStreams = self.playlistService.getStreamsByPlaylistId(_playlist.id)

        if(len(_rawStreams) == 0):
            printS("Playlist \"", _playlist.name, "\" has ", len(_streams), " streams, but they could not be found in database (they may have been removed). Ending playback.")
            return False

        if(shuffle):
            _streams = random.shuffle(_rawStreams)
        else:
            _streams = _rawStreams[startIndex:]

        printS("Playing playlist ", _playlist.name, ".")
        printS("Starting at stream number: ", (startIndex + 1), ", shuffle is ", ("on" if shuffle else "off"), ", repeat playlist is ", ("on" if repeatPlaylist else "off"), ", played videos set to watched is ", ("on" if PLAYED_ALWAYS_WATCHED else "off"), ".")

        _playResult = False
        try:
            if(True): # Playlist mode
                _playResult = self.playCmd(_playlist, _streams)
        except:
            if(self.debug): printS(sys.exc_info(), color=colors["WARNING"])
            #printS("handleing of streams encountered an issue.", color=colors["WARNING"])

        printS("Playlist \"", _playlist.name, "\" finished.")

        if(repeatPlaylist):
            self.play(playlistId, startIndex, shuffle, repeatPlaylist)

        return _playResult
    
    def playCmd(self, playlist: Playlist, streams: List[QueueStream]) -> bool:
        """
        Use CLI when playing from playback.

        Args:
            playlist (Playlist): Playlist which is currently playing
            streams (List[QueueStream]): QueueStreams to play from Playlist playlist

        Returns:
            bool: finished = True
        """
        
        for i, stream in enumerate(streams):
            if(stream.watched != None and not playlist.playWatchedStreams):
                _checkLogsMessage = " Check your logs (" + WATCHED_LOG_FILEPATH + ") for date/time watched." if LOG_WATCHED else " Logging is disabled and date/time watched is not available."
                printS("Stream \"", stream.name, "\" (ID: ", stream.id, ") has been marked as watched.", _checkLogsMessage, color = colors["WARNING"])
                continue

            subprocessStream = None
            if(stream.isWeb):
                subprocessStream = subprocess.Popen(f"call start {stream.uri}", stdout=subprocess.PIPE, shell=True) # PID set by this is not PID of browser, just subprocess which opens browser
                
                # https://stackoverflow.com/questions/7989922/opening-a-process-with-popen-and-getting-the-pid
                # subprocessStream = subprocess.Popen([BROWSER_BIN, f"{stream.uri}"], stdout=subprocess.PIPE, shell=False) # PID set by this SHOULD be browser, but is not
            else:
                # TODO
                printS("Non-web streams currently not supported, skipping video ", stream.name, color = colors["ERROR"])
                continue

            printS(f"{i} - Now playing \"{stream.name}\"" + ("..." if(i < (len(streams) - 1)) else ". This is the last stream in this playback, press enter to finish."), color = colors["BOLD"])
            _inputHandleing = self.handlePlaybackInput(playlist, stream)
            if(_inputHandleing == 0):
                printS("An error occurred while parsing inputs.", color = colors["ERROR"])
                return False
            elif(_inputHandleing == 1):
                pass
            elif(_inputHandleing == 2):
                continue
            elif(_inputHandleing == 3):
                break
            
            # subprocessStream.terminate() # TODO Doesn't seem to work with browser, at least not new tabs
            
            now = datetime.now()
            if(LOG_WATCHED and len(WATCHED_LOG_FILEPATH) > 0):
                logLine = f"{str(now)} - Playlist \"{playlist.name}\" (ID: {playlist.id}), watched video \"{stream.name}\" (ID: {stream.id})\n" 
                with open(WATCHED_LOG_FILEPATH, "a") as file:
                    file.write(logLine)
                    
            if(PLAYED_ALWAYS_WATCHED):
                stream.watched = now
                
                _updateSuccess = self.queueStreamService.update(stream)
                if(not _updateSuccess):
                    printS("Stream \"", stream.name, "\" could not be updated as watched.", color=colors["WARNING"])
                    
        return True

    def handlePlaybackInput(self, playlist: Playlist, stream: QueueStream) -> int:
        """
        Handles user input and returns an int code for what the calling method should do regarding it's own loop.
        
        Args:
            playlist (Playlist): Playlist currently playing
            stream (QueueStream): QueueStream currently playing
            
        Return codes: 
        0 - Error, internal loop failed to return any other code
        1 - No action needed, parent loop should be allowed to finish as normal
        2 - continue parent loop
        3 - break parent loop 
        """
        
        while 1: # Infinite loop until a return is hit
            _inputMessage = "\tPress enter to play next, \"skip\" to skip video, or \"quit\" to quit playback: "
            _input = input(_inputMessage)
                
            if(_input.strip() == ""):
                return 1
            elif(len(self.quitInputs) > 0 and _input in self.quitInputs):
                printS("Ending playback due to user input.", color = colors["OKGREEN"])
                return 3
            elif(len(self.skipInputs) > 0 and _input in self.skipInputs):
                printS("Skipping video, will not be marked as watched.", color = colors["OKGREEN"])
                return 2
            elif(len(self.addToInputs) > 0 and " " in _input and _input.split(" ")[0] in self.addToInputs):
                _idsIndices = _input.split(" ")[1:]
                _crossAddPlaylistResult = self.addPlaybackStreamToPlaylist(stream, _idsIndices)
                printS("Stream added to Playlist \"", playlist.name, "\".", color = colors["OKGREEN"], doPrint = (_crossAddPlaylistResult > 0))
                printS("Stream could not be added to Playlist \"", playlist.name, "\".", color = colors["FAIL"], doPrint = (_crossAddPlaylistResult == 0))
            else:
                printS("Argument(s) not recognized: \"", _input, "\".", color = colors["WARNING"])
        
        return 0

    def addPlaybackStreamToPlaylist(self, queueStream: QueueStream, idsIndices: List[str]) -> int:
        """
        Add the QueueStream currently playing in playback, to another Playlist.

        Args:
            queueStream (QueueStream): QueueStream to add
            idsIndices (List[str]): ID or index of Playlist to add stream to

        Returns:
            int: number of Playlists stream was added to
        """
        
        if(len(idsIndices) < 1):
            printS("Missing arguments, cross-adding stream requires IDs of Playlists to add to.", color=colors["WARNING"])
            return 0
        
        _ids = self.utility.getIdsFromInput(idsIndices, self.playlistService.getAllIds(), self.playlistService.getAll())
        if(len(_ids) == 0):
            printS("Failed to add cross-add streams, missing playlistIds or indices.", color = colors["WARNING"])
            return 0
        
        _result = 0
        for _id in _ids:
            _addResult = self.playlistService.addStreams(_id, [queueStream])
            if(_addResult):
                _result += 1
        
        return _result