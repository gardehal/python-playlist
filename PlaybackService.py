import os
import random
import subprocess
import sys
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from grdUtil.BashColor import BashColor
from grdUtil.InputUtil import getIdsFromInput, sanitize
from grdUtil.PrintUtil import printS, printLists, printStack

from model.Playlist import Playlist
from model.QueueStream import QueueStream
from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService
from StreamSourceService import StreamSourceService
from Utility import Utility

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
    utility: Utility = None
    storagePath: str = LOCAL_STORAGE_PATH
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    quitInputs: List[str] = None
    skipInputs: List[str] = None
    addToInputs: List[str] = None
    printDetailsInputs: List[str] = None

    def __init__(self):
        self.playlistService: PlaylistService = PlaylistService()
        self.queueStreamService: QueueStreamService = QueueStreamService()
        self.streamSourceService: StreamSourceService = StreamSourceService()
        self.utility: Utility = Utility()
        self.quitInputs: List[str] = self.utility.quitArguments
        self.skipInputs: List[str] = self.utility.skipArguments
        self.repeatInputs: List[str] = self.utility.repeatArguments
        self.listPlaylistInputs: List[str] = self.utility.listPlaylistArguments
        self.addToInputs: List[str] = self.utility.addCurrentToPlaylistArguments
        self.printDetailsInputs: List[str] = self.utility.printPlaybackDetailsArguments
        self.printHelpInputs: List[str] = self.utility.printPlaybackHelpArguments

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

        _streams = _rawStreams[startIndex:]
        if(shuffle):
            random.shuffle(_streams)

        printS("Playing playlist ", _playlist.name, ".")
        printS("Starting at stream number: ", (startIndex + 1), ", shuffle is ", ("on" if shuffle else "off"), ", repeat playlist is ", ("on" if repeatPlaylist else "off"), ", played videos set to watched is ", ("on" if PLAYED_ALWAYS_WATCHED else "off"), ".")

        _playResult = False
        try:
            if(True): # Playlist mode
                _playResult = self.playCmd(_playlist, _streams)
        except:
            printStack(doPrint = DEBUG)

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
                printS("Stream \"", stream.name, "\" (ID: ", stream.id, ") has been marked as watched.", _checkLogsMessage, color = BashColor.WARNING)
                continue

            subprocessStream = None
            if(stream.isWeb):
                subprocessStream = subprocess.Popen(f"call start {stream.uri}", stdout=subprocess.PIPE, shell=True) # PID set by this is not PID of browser, just subprocess which opens browser
                
                # https://stackoverflow.com/questions/7989922/opening-a-process-with-popen-and-getting-the-pid
                # subprocessStream = subprocess.Popen([BROWSER_BIN, f"{stream.uri}"], stdout=subprocess.PIPE, shell=False) # PID set by this SHOULD be browser, but is not
            else:
                # TODO
                printS("Non-web streams currently not supported, skipping video ", stream.name, color = BashColor.ERROR)
                continue

            printS(f"{i} - Now playing \"{stream.name}\"" + ("..." if(i < (len(streams) - 1)) else ". This is the last stream in this playback, press enter to finish."), color = BashColor.BOLD)
            _inputHandleing = self.handlePlaybackInput(playlist, stream)
            if(_inputHandleing == 0):
                printS("An error occurred while parsing inputs.", color = BashColor.ERROR)
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
                    printS("Stream \"", stream.name, "\" could not be updated as watched.", color=BashColor.WARNING)
                    
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
            self.skipInputs.append("skip") # Ensure skip and quit always available
            self.quitInputs.append("quit")
            _input = sanitize(input(_inputMessage), mode = 2)
                
            if(_input.strip() == ""):
                return 1
            
            elif(len(self.skipInputs) > 0 and _input in self.skipInputs):
                printS("Skipping video, will not be marked as watched.", color = BashColor.OKGREEN)
                return 2
            
            elif(len(self.quitInputs) > 0 and _input in self.quitInputs):
                printS("Ending playback due to user input.", color = BashColor.OKGREEN)
                return 3
            
            elif(len(self.repeatInputs) > 0 and _input in self.repeatInputs):
                printS("Repeating stream.", color = BashColor.OKGREEN)
                self.playCmd(playlist, [stream]) # A little weird with prints and continueing but it works
            
            elif(len(self.listPlaylistInputs) > 0 and _input in self.listPlaylistInputs):
                _result = self.playlistService.getAll()
                if(len(_result) > 0):
                    _nPlaylists = len(_result)
                    _title = "\t" + str(_nPlaylists) + " Playlist(s)."
                    
                    _data = []
                    for (i, _entry) in enumerate(_result):
                        _data.append("\t" + str(i) + " - " + _entry.summaryString())
                        
                    printLists([_data], [_title])
                else:
                    printS("No Playlists found.", color = BashColor.WARNING)
            
            elif(len(self.addToInputs) > 0 and " " in _input and _input.split(" ")[0] in self.addToInputs):
                _idsIndices = _input.split(" ")[1:]
                _crossAddPlaylistResult = self.addPlaybackStreamToPlaylist(stream, _idsIndices)
                printS("QueueStream \"", stream.name, "\" added to new Playlist \"", _crossAddPlaylistResult[0].name, "\".", color = BashColor.OKGREEN, doPrint = (len(_crossAddPlaylistResult) > 0))
                printS("QueueStream \"", stream.name, "\" could not be added to new Playlist.", color = BashColor.FAIL, doPrint = (len(_crossAddPlaylistResult) == 0))
                
            elif(len(self.printDetailsInputs) > 0 and _input in self.printDetailsInputs):
                self.playlistService.printPlaylistDetails([playlist.id])
                
            elif(len(self.printHelpInputs) > 0 and _input in self.printHelpInputs):
                _help = self.utility.getPlaylistArgumentsHelpString()
                printS(_help)
                
            else:
                printS("Argument(s) not recognized: \"", _input, "\". Please refrain from using arrows to navigate in the CLI as it adds hidden characters.", color = BashColor.WARNING)
            
        return 0

    def addPlaybackStreamToPlaylist(self, queueStream: QueueStream, idsIndices: List[str]) -> List[Playlist]:
        """
        Add the QueueStream currently playing in playback, to another Playlist.

        Args:
            queueStream (QueueStream): QueueStream to add
            idsIndices (List[str]): ID or index of Playlist to add stream to

        Returns:
            Playlist: Playlist the stream was added to
        """
        
        _result = []
        if(len(idsIndices) < 1):
            printS("Missing arguments, cross-adding stream requires IDs of Playlists to add to.", color = BashColor.WARNING)
            return _result
        
        _ids = getIdsFromInput(idsIndices, self.playlistService.getAllIds(), self.playlistService.getAll(), debug = DEBUG)
        if(len(_ids) == 0):
            printS("Failed to add cross-add streams, missing playlistIds or indices.", color = BashColor.WARNING)
            return _result
        
        for _id in _ids:
            _addResult = self.playlistService.addStreams(_id, [queueStream])
            if(len(_addResult) > 0):
                _playlist = self.playlistService.get(_id)
                _result.append(_playlist)
        
        return _result
