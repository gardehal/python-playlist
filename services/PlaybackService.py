import os
import random
import subprocess
import uuid
from copy import copy
from typing import List

from Commands import Commands
from dotenv import load_dotenv
from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTime
from grdUtil.InputUtil import getIdsFromInput, sanitize
from grdUtil.PrintUtil import printD, printLists, printS, printStack
from model.Playlist import Playlist
from model.QueueStream import QueueStream

from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.StreamSourceService import StreamSourceService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")
LOG_WATCHED = eval(os.environ.get("LOG_WATCHED"))
DOWNLOAD_WEB_STREAMS = eval(os.environ.get("DOWNLOAD_WEB_STREAMS"))
REMOVE_WATCHED_ON_FETCH = eval(os.environ.get("REMOVE_WATCHED_ON_FETCH"))
PLAYED_ALWAYS_WATCHED = eval(os.environ.get("PLAYED_ALWAYS_WATCHED"))
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")
LOG_DIR_PATH = os.environ.get("LOG_DIR_PATH")
LOG_LEVEL = os.environ.get("LOG_LEVEL")
BROWSER_BIN = os.environ.get("BROWSER_BIN")

class PlaybackService():
    commands: Commands = None
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
        self.commands: Commands = Commands()
        self.quitInputs: List[str] = self.commands.quitArguments
        self.skipInputs: List[str] = self.commands.skipArguments
        self.repeatInputs: List[str] = self.commands.repeatArguments
        self.listPlaylistInputs: List[str] = self.commands.listPlaylistArguments
        self.addToInputs: List[str] = self.commands.addCurrentToPlaylistArguments
        self.printDetailsInputs: List[str] = self.commands.printPlaybackDetailsArguments
        self.printHelpInputs: List[str] = self.commands.printPlaybackHelpArguments

    def play(self, playlistId: str, startIndex: int = 0, shuffle: bool = False, repeatPlaylist: bool = False) -> bool:
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

        playlist = self.playlistService.get(playlistId)
        if(playlist == None):
            printD("Playlist with ID ", playlistId, " was not found.", doPrint = DEBUG)
            return False

        if(len(playlist.streamIds) == 0):
            printS("No streams found in \"", playlist.name, "\". Ending playback.")
            return False

        streams = []
        rawStreams = self.playlistService.getStreamsByPlaylistId(playlist.id)

        if(len(rawStreams) == 0):
            printS("Playlist \"", playlist.name, "\" has ", len(streams), " streams, but they could not be found in database (they may have been removed). Ending playback.")
            return False

        streams = rawStreams[startIndex:]
        if(shuffle):
            random.shuffle(streams)

        printS("Playing ", playlist.name, ".")
        printS("Starting at stream number: ", (startIndex + 1), ", shuffle is ", ("on" if shuffle else "off"), ", repeat playlist is ", ("on" if repeatPlaylist else "off"), ", played videos set to watched is ", ("on" if PLAYED_ALWAYS_WATCHED else "off"), ".")

        playResult = 0
        try:
            if(True): # Play in CLI mode
                playResult = self.playCli(playlist, streams)
        except:
            printStack(doPrint = DEBUG)
            
        resultPrint = ""
        if(PLAYED_ALWAYS_WATCHED):
            resultPrint = f", {playResult}/{len(playlist.streamIds)} QueueStreams watched"
            
        printS("Playlist \"", playlist.name, "\" finished", resultPrint, ".")

        if(repeatPlaylist):
            return self.play(playlistId, startIndex, shuffle, repeatPlaylist)

        return True
    
    def playCli(self, playlist: Playlist, streams: List[QueueStream]) -> int:
        """
        Use CLI when playing from playback.

        Args:
            playlist (Playlist): Playlist which is currently playing.
            streams (List[QueueStream]): QueueStreams to play from Playlist playlist.

        Returns:
            int: Number of streams watched.
        """
        
        nWatched = 0
        for i, stream in enumerate(streams):
            if(stream.watched != None and not playlist.playWatchedStreams):
                checkLogsMessage = " Check your logs (" + WATCHED_LOG_FILEPATH + ") for date/time watched." if LOG_WATCHED else " Logging is disabled and date/time watched is not available."
                printS("Stream \"", stream.name, "\" (ID: ", stream.id, ") has been marked as watched.", checkLogsMessage, color = BashColor.WARNING)
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
            inputHandleing = self.handlePlaybackInput(playlist, stream)
            if(inputHandleing == 0):
                printS("An error occurred while parsing inputs.", color = BashColor.ERROR)
                return False
            elif(inputHandleing == 1):
                pass
            elif(inputHandleing == 2):
                continue
            elif(inputHandleing == 3):
                break
            
            # subprocessStream.terminate() # TODO Doesn't seem to work with browser, at least not new tabs
            
            now = getDateTime()
            if(LOG_WATCHED and len(WATCHED_LOG_FILEPATH) > 0):
                logLine = f"{str(now)} - Playlist \"{playlist.name}\" (ID: {playlist.id}), watched video \"{stream.name}\" (ID: {stream.id})\n" 
                with open(WATCHED_LOG_FILEPATH, "a") as file:
                    file.write(logLine)
                    
            if(PLAYED_ALWAYS_WATCHED):
                stream.watched = now
                
                updateSuccess = self.queueStreamService.update(stream)
                if(updateSuccess):
                    nWatched += 1
                else:
                    printS("\"", stream.name, "\" could not be updated as watched.", color=BashColor.WARNING)
                    
        return nWatched

    def handlePlaybackInput(self, playlist: Playlist, stream: QueueStream) -> int:
        """
        Handles user input and returns an int code for what the calling method should do regarding it's own loop.
        
        Args:
            playlist (Playlist): Playlist currently playing.
            stream (QueueStream): QueueStream currently playing.
            
        Return codes: 
        0 - Error, internal loop failed to return any other code.
        1 - No action needed, parent loop should be allowed to finish as normal.
        2 - continue parent loop.
        3 - break parent loop.
        """
        
        while 1: # Infinite loop until a return is hit
            inputMessage = "\tAwaiting input: "
            self.quitInputs.append("quit") # Ensure quit and help always available
            self.printHelpInputs.append("help")
            inputArgs = sanitize(input(inputMessage).strip(), mode = 2)
                
            if(inputArgs == ""):
                return 1
            
            elif(len(self.skipInputs) > 0 and inputArgs in self.skipInputs):
                printS("Skipping.", color = BashColor.OKGREEN)
                return 2
            
            elif(len(self.quitInputs) > 0 and inputArgs in self.quitInputs):
                return 3
            
            elif(len(self.repeatInputs) > 0 and inputArgs in self.repeatInputs):
                printS("Repeating.", color = BashColor.OKGREEN)
                self.playCli(playlist, [stream]) # A little weird with prints and continuing but it works
            
            elif(len(self.listPlaylistInputs) > 0 and inputArgs in self.listPlaylistInputs):
                result = self.playlistService.getAll()
                if(len(result) > 0):
                    nPlaylists = len(result)
                    title = "\t" + str(nPlaylists) + " Playlist(s)."
                    
                    data = []
                    for (i, entry) in enumerate(result):
                        data.append("\t" + str(i) + " - " + entry.summaryString())
                        
                    printLists([data], [title])
                else:
                    printS("No Playlists found.", color = BashColor.WARNING)
            
            elif(len(self.addToInputs) > 0 and " " in inputArgs and inputArgs.split(" ")[0] in self.addToInputs):
                idsIndices = inputArgs.split(" ")[1:]
                crossAddPlaylistResult = self.addPlaybackStreamToPlaylist(stream, idsIndices)
                if(len(crossAddPlaylistResult) > 0):
                    printS("\"", stream.name, "\" added to \"", crossAddPlaylistResult[0].name, "\".", color = BashColor.OKGREEN)
                else:
                    printS("\"", stream.name, "\" could not be added to any playlists.", color = BashColor.FAIL, doPrint = (len(crossAddPlaylistResult) == 0))
                
            elif(len(self.printDetailsInputs) > 0 and inputArgs in self.printDetailsInputs):
                self.playlistService.printPlaylistDetails([playlist.id])
                
            elif(len(self.printHelpInputs) > 0 and inputArgs in self.printHelpInputs):
                help = self.commands.getPlaylistArgumentsHelpString()
                printS(help)
                
            else:
                printS("Argument(s) not recognized: \"", inputArgs, "\". Try \"help\" for help.", color = BashColor.WARNING)
            
        return 0

    def addPlaybackStreamToPlaylist(self, queueStream: QueueStream, idsIndices: List[str]) -> List[Playlist]:
        """
        Add the QueueStream currently playing in playback, to another Playlist.

        Args:
            queueStream (QueueStream): QueueStream to add.
            idsIndices (List[str]): ID or index of Playlist to add stream to.

        Returns:
            Playlist: Updated Playlist the stream was added to.
        """
        
        result = []
        if(len(idsIndices) < 1):
            printS("Missing arguments, cross-adding stream requires IDs of Playlists to add to.", color = BashColor.WARNING)
            return result
        
        ids = getIdsFromInput(idsIndices, self.playlistService.getAllIds(), self.playlistService.getAll(), debug = DEBUG)
        if(len(ids) == 0):
            printS("Failed to add cross-add streams, missing playlistIds or indices.", color = BashColor.WARNING)
            return result
        
        for id in ids:
            newQueueStream = copy(queueStream)
            newQueueStream.id = str(uuid.uuid4())
            addResult = self.playlistService.addStreams(id, [newQueueStream])
            if(len(addResult) > 0):
                playlist = self.playlistService.get(id)
                result.append(playlist)
        
        return result
