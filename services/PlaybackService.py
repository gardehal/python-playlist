import random
import re
import subprocess
import uuid
from copy import copy
from typing import List

from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTime
from grdUtil.InputUtil import getIdsFromInput, isNumber, sanitize
from grdUtil.PrintUtil import printD, printLists, printS, printStack
from psutil import Popen

from Commands import Commands
from enums.StreamSourceType import StreamSourceType, StreamSourceTypeUtil
from model.PlaybackInput import PlaybackInput
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.StreamSourceService import StreamSourceService
from Settings import Settings


class PlaybackService():
    commands: Commands = None
    settings: Settings = None
    storagePath: str = None
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    quitInputs: List[str] = None
    quitWatchedInputs: List[str] = None
    skipInputs: List[str] = None
    addToInputs: List[str] = None
    circumventRestricted: List[str] = None
    printDetailsInputs: List[str] = None

    def __init__(self):
        self.commands = Commands()
        self.settings = Settings()
        self.storagePath = self.settings.localStoragePath
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.streamSourceService = StreamSourceService()
        self.quitInputs = self.commands.quitArguments
        self.quitWatchedInputs = self.commands.quitWatchedArguments
        self.skipInputs = self.commands.skipArguments
        self.repeatInputs = self.commands.repeatArguments
        self.listPlaylistInputs = self.commands.listPlaylistArguments
        self.addToInputs = self.commands.addCurrentToPlaylistArguments
        self.circumventRestricted = self.commands.circumventRestricted
        self.printDetailsInputs = self.commands.printPlaybackDetailsArguments
        self.nextInputs = self.commands.nextArguments
        self.printHelpInputs = self.commands.printPlaybackHelpArguments

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
            printD("Playlist with ID ", playlistId, " was not found.", debug = self.settings.debug)
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

        printS("Playing ", playlist.name, " (", len(streams),  " streams total).")
        printS("Starting at stream number: ", (startIndex + 1), ", shuffle is ", ("on" if shuffle else "off"), ", repeat playlist is ", ("on" if repeatPlaylist else "off"), ", played videos set to watched is ", ("on" if self.settings.playedAlwaysWatched else "off"), ".")

        playResult = 0
        try:
            if(True): # Play in CLI mode
                playResult = self.playCli(playlist, streams)
        except:
            printStack(doPrint = self.settings.debug)
            
        resultPrint = ""
        if(self.settings.playedAlwaysWatched):
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
        streamsToSkip = 0
        streamsIndex = playlist.streamIds.index(streams[0].id)
        for i, stream in enumerate(streams):
            streamsIndex += 1
            
            if(streamsToSkip > 0):
                streamsToSkip = streamsToSkip - 1
                printS("Skipping \"", stream.name, "\".", color = BashColor.OKGREEN)
                continue
            
            if(stream.watched != None and not playlist.playWatchedStreams):
                checkLogsMessage = " Check your logs (" + self.settings.watchedLogFilepath + ") for date/time watched." if self.settings.logWatched else " Logging is disabled and date/time watched is not available."
                printS("Stream \"", stream.name, "\" (ID: ", stream.id, ") has been marked as watched.", checkLogsMessage, color = BashColor.WARNING)
                continue

            subprocessStream = None
            if(stream.isWeb):
                subprocessStream = self.openQueueStreamBrowser(stream.uri)
            else:
                # TODO
                printS("Non-web streams currently not supported, skipping video ", stream.name, color = BashColor.FAIL)
                continue

            padI = str(streamsIndex).rjust(4, " ")
            playingContinued = "..." if(i <= (len(streams))) else ". This is the last stream in this playback, press enter to finish."
            printS(padI, " - Now playing \"", stream.name, "\"" + playingContinued, color = BashColor.BOLD)
            inputHandling = self.handlePlaybackInput(playlist, stream)
            if(inputHandling == 0):
                printS("An error occurred while parsing inputs.", color = BashColor.FAIL)
                return False
            elif(inputHandling.code == 1):
                pass
            elif(inputHandling.code == 2):
                streamsToSkip = inputHandling.nSkip
                continue
            elif(inputHandling.code == 3):
                break
            
            # subprocessStream.terminate() # TODO Doesn't seem to work with browser, at least not new tabs
            
            now = getDateTime()
            if(self.settings.logWatched and len(self.settings.watchedLogFilepath) > 0):
                logLine = f"{str(now)} - Playlist \"{playlist.name}\" (ID: {playlist.id}), watched video \"{stream.name}\" (ID: {stream.id})\n" 
                with open(self.settings.watchedLogFilepath, "a") as file:
                    file.write(logLine)
                    
            if(self.settings.playedAlwaysWatched):
                stream.watched = now
                
                updateSuccess = self.queueStreamService.update(stream)
                if(updateSuccess):
                    nWatched += 1
                else:
                    printS("\"", stream.name, "\" could not be updated as watched.", color=BashColor.ERROR)
            
            if(inputHandling.code == 4):
                break
            
        return nWatched
    
    def openQueueStreamBrowser(self, url: str) -> Popen:
        """
        Open a URL in the browser.

        Args:
            url (str): url to open.

        Returns:
            Popen: PID if new process created. (?)
        """
        
        return subprocess.Popen(f"call start {url}", stdout=subprocess.PIPE, shell=True) # PID set by this is not PID of browser, just subprocess which opens browser
        
        # https://stackoverflow.com/questions/7989922/opening-a-process-with-popen-and-getting-the-pid
        # return subprocess.Popen([self.settings.browserBin, f"{stream.uri}"], stdout=subprocess.PIPE, shell=False) # PID set by this SHOULD be browser, but is not

    def handlePlaybackInput(self, playlist: Playlist, stream: QueueStream) -> PlaybackInput:
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
        4 - break parent loop later.
        
        Returns:
            PlaybackInput: Object with code and other arguments.
        """
        
        while 1: # Infinite loop until a return is hit
            inputMessage = "\tAwaiting input: "
            self.quitInputs.append("quit") # Ensure quit and help always available
            self.printHelpInputs.append("help")
            inputArgs = sanitize(input(inputMessage).strip(), mode = 2)
                
            if(inputArgs == ""):
                return PlaybackInput(1)
            
            elif((len(self.skipInputs) > 0 and inputArgs in self.skipInputs) or (" " in inputArgs and inputArgs.split(" ")[0] in self.skipInputs)):
                if(" " not in inputArgs):
                    printS("Skipping stream...", color = BashColor.OKGREEN)
                    return PlaybackInput(2, 0)
                
                nSkip = inputArgs.split(" ")[1]
                if(len(nSkip) > 0 and isNumber(nSkip, intOnly = True)):
                    nSkipInt = int(nSkip)
                    if(nSkipInt <= 0):
                        printS("Cannot not skip 0 or fewer streams.", color = BashColor.FAIL)
                        continue
                    
                    printS("Skipping ", nSkipInt, " stream(s)...", color = BashColor.OKGREEN)
                    return PlaybackInput(2, nSkipInt - 1)
                else:
                    printS("Could not skip multiple streams, \"", nSkip, "\" is not a number.", color = BashColor.FAIL)
                    continue
            
            elif(len(self.quitInputs) > 0 and inputArgs in self.quitInputs):
                return PlaybackInput(3)
            
            elif(len(self.quitWatchedInputs) > 0 and inputArgs in self.quitWatchedInputs):
                return PlaybackInput(4)
            
            elif(len(self.repeatInputs) > 0 and inputArgs in self.repeatInputs):
                printS("Repeating.", color = BashColor.OKGREEN)
                self.playCli(playlist, [stream]) # A little weird with prints and continuing but it works
            
            elif(len(self.listPlaylistInputs) > 0 and inputArgs in self.listPlaylistInputs):
                result = self.playlistService.getAllSorted()
                if(len(result) > 0):
                    nPlaylists = len(result)
                    title = "\t" + str(nPlaylists) + " Playlist(s)."
                    
                    data = []
                    for (i, entry) in enumerate(result):
                        favorite = " "
                        if(entry.favorite):
                            favorite = "*"
                            
                        padI = str(i + 1).rjust(4, " ")
                        data.append(padI + " - " + favorite + entry.summaryString())
                        
                    printLists([data], [title])
                else:
                    printS("No Playlists found.", color = BashColor.WARNING)
            
            elif(len(self.addToInputs) > 0 and " " in inputArgs and inputArgs.split(" ")[0] in self.addToInputs):
                idsIndices = inputArgs.split(" ")[1:]
                crossAddPlaylistResult = self.addPlaybackStreamToPlaylist(stream, idsIndices)
                if(len(crossAddPlaylistResult) > 0):
                    printS("\"", stream.name, "\" added to \"", crossAddPlaylistResult[0].name, "\".", color = BashColor.OKGREEN)
                else:
                    printS("\"", stream.name, "\" could not be added to any playlists.", color = BashColor.FAIL)
                
            elif(len(self.circumventRestricted) > 0 and inputArgs in self.circumventRestricted):
                self.openRestricted(stream)
            
            elif(len(self.printDetailsInputs) > 0 and inputArgs in self.printDetailsInputs):
                self.playlistService.printPlaylistDetails([playlist.id])
                
            elif(len(self.nextInputs) > 0 and inputArgs in self.nextInputs):
                streamStartIndex = playlist.streamIds.index(stream.id) + 1
                self.playlistService.printPlaylistShort([playlist.id], streamStartIndex = streamStartIndex)
                
            elif(len(self.printHelpInputs) > 0 and inputArgs in self.printHelpInputs):
                help = self.commands.getPlaylistArgumentsHelpString()
                printS(help)
                
            else:
                printS("Argument(s) not recognized: \"", inputArgs, "\". Try \"help\" for help.", color = BashColor.WARNING)
            
        return PlaybackInput(0)

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
        
        ids = getIdsFromInput(idsIndices, self.playlistService.getAllIdsSorted(), self.playlistService.getAllSorted(), startAtZero = False, debug = self.settings.debug)
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

    def openRestricted(self, queueStream: QueueStream) -> bool:
        """
        Circumvent the restrictions on videos, for example age restriction on YouTube, which blocks watching if the watcher is not logged in.

        Args:
            queueStream (QueueStream): QueueStream to watch.

        Returns:
            bool: Result of circumvent.
        """
        
        streamSourceType = StreamSourceTypeUtil.strToStreamSourceType(queueStream.uri)
        if(streamSourceType.value == StreamSourceType.YOUTUBE.value):
            id = self.getYouTubeId(queueStream.uri)
            url = f"https://www.nsfwyoutube.com/watch?v={id}"
            self.openQueueStreamBrowser(url)
            return True
        else:
            sourceType = streamSourceType.name.capitalize()
            printS("No circumvent implemented for ", sourceType, ".", color = BashColor.WARNING)
        
        return False

    def getYouTubeId(self, url: str) -> str:
        """
        Get YouTube ID from URL.

        Args:
            url (str): URL with ID to get,

        Returns:
            str | None: ID if URL is valid format.
        """
        
        if("youtu.be/" in url):
            return re.search(r"youtu\.be\/(\w+)", url).group(1)
        elif("youtube.com/watch?v=" in url):
            return re.search(r"\/watch\?v=(\w+)", url).group(1)
        else:
            return None
        