import os
import sys
from typing import List

from dotenv import load_dotenv
from myutil.Util import *
from QueueStreamService import QueueStreamService

from FetchService import FetchService
from PlaylistService import PlaylistService
from StreamSourceService import StreamSourceService
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource

os.system("") # Needed to "trigger" coloured text

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")
LOG_WATCHED = eval(os.environ.get("LOG_WATCHED"))
DOWNLOAD_WEB_STREAMS = eval(os.environ.get("DOWNLOAD_WEB_STREAMS"))
REMOVE_WATCHED_ON_FETCH = eval(os.environ.get("REMOVE_WATCHED_ON_FETCH"))
PLAYED_ALWAYS_WATCHED = eval(os.environ.get("PLAYED_ALWAYS_WATCHED"))
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")
BROWSER_BIN = os.environ.get("BROWSER_BIN")

# General
helpFlags = ["-help", "-h"]
testFlags = ["-test", "-t"]
# Playlist
addPlaylistFlags = ["-addplaylist", "-apl", "-ap"]
removePlaylistFlags = ["-removeplaylist", "-rmpl", "-rpl", "-rmp", "-rp"]
listPlaylistFlags = ["-listplaylist", "-lpl", "-lp"]
fetchPlaylistSourcesFlags = ["-fetch", "-f", "-update", "-u"]
prunePlaylistFlags = ["-prune", "-p"]
playFlags = ["-play", "-p"]
# Stream
addStreamFlags = ["-add", "-a"]
removeStreamFlags = ["-remove", "-rm", "-r"]
# Sources
listSourcesFlags = ["-listsources", "-ls"]
addSourcesFlags = ["-addsource", "-as"]
removeSourceFlags = ["-removesource", "-rms", "-rs"]
# Meta
listSettingsFlags = ["-settings", "-secrets", "-s"]

class Main:
    def main():
        argC = len(sys.argv)
        argV = sys.argv
        argIndex = 1

        if(argC < 2):
            Main.printHelp()

        fetchService = FetchService()
        playlistService = PlaylistService()
        queueStreamService = QueueStreamService()
        streamSourceService = StreamSourceService()
        makeFiles(WATCHED_LOG_FILEPATH)

        while argIndex < argC:
            arg = sys.argv[argIndex].lower()

            if(arg in helpFlags):
                Main.printHelp()

            elif(arg in testFlags):
                _input = extractArgs(argIndex, argV)
                printS("Test", color = colors["OKBLUE"])
                
                if(1):
                    sourceId = "03dc9d59-bd52-447f-b373-a35e1453c6f4"
                    playlistId = "1154dd04-cbc8-4fcd-8f8a-ccca0b71dd05"
                    # print(streamSourceService.add(StreamSource("Mocked source", "https://www.youtube.com/channel/UCFtc3XdXgLFwhlDajMGK69w", True, 2, True)))
                    # print(playlistService.add(Playlist("Mocked playlist", [], None, 0, True, True, [sourceId])))
                    print(fetchService.fetch(playlistId))
                    # print(playlistService.playCmd(playlistId))
                    
                quit()

            # Playlist
            elif(arg in addPlaylistFlags):
                # Expected input: name, playWatchedStreams?, allowDuplicates?, streamSourceIds/indices?
                _input = extractArgs(argIndex, argV)
                _name = str(_input[0]) if len(_input) > 0 else "New playlist"
                _playWatchedStreams = eval(_input[1]) if len(_input) > 1 else True
                _allowDuplicates = eval(_input[2]) if len(_input) > 2 else True
                _streamSourceIds = Main.getIdsFromInput(_input[3:], playlistService) if len(_input) > 3 else [] # Issue in function with call to self.GetAll in service, self not defined because of passing service as arg?
                    
                _entity = Playlist(name = _name, playWatchedStreams = _playWatchedStreams, allowDuplicates = _allowDuplicates, streamSourceIds = _streamSourceIds)
                _result = playlistService.add(_entity)
                if(_result != None):
                    printS("Playlist added successfully with ID \"", _result.id, "\".", color=colors["OKGREEN"])
                else:
                    printS("Failed to create playlist. See rerun command with -help to see expected arguments.", color=colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in removePlaylistFlags):
                # Expected input: playlistId
                _input = extractArgs(argIndex, argV)
                _id = str(_input[0]) if len(_input) > 0 else None

                _result = playlistService.remove(_id)
                if(_result):
                    printS("Playlist removed successfully.", color=colors["OKGREEN"])
                else:
                    printS("Failed to remove playlist. See rerun command with -help to see expected arguments.", color=colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in listPlaylistFlags):
                # Expected input: None

                _result = playlistService.getAll()
                if(len(_result) > 0):
                    for (i, _entry) in enumerate(_result):
                        printS((i + 1), " - ", _entry.summaryString())
                else:
                    printS("Playlist removed successfully.", color=colors["OKGREEN"])

                argIndex += 1
                continue

            elif(arg in fetchPlaylistSourcesFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            elif(arg in prunePlaylistFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            elif(arg in playFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            # Streams
            elif(arg in addStreamFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            elif(arg in removeStreamFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            # Sources
            elif(arg in listSourcesFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            elif(arg in addSourcesFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            elif(arg in removeSourceFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            # Settings
            elif(arg in listSettingsFlags):
                Main.printSettings()

                argIndex += 1
                continue

            # Invalid, inform and quit
            else:
                printS("Argument not recognized: \"", arg, "\", please see documentation or run with \"-help\" for help.", color=colors["WARNING"])

            argIndex += 1
            
    def getIdsFromInput(input: List[str], service: object) -> List[str]:
        """
        Get IDs from a list of inputs, whether they are raw IDs that must be checked via the database or indices (formatted "i[index]") of a list.

        Args:
            input (List[str]): input if IDs/indices
            service (object): class which has a function getAllIds() with IDs to check against

        Returns:
            List[str]: List of existing IDs for input which can be found
        """
        
        _result = []
        _existingIds = service.getAllIds()
        for _string in input:
            if(_string[0] == "i"): #starts with "i", like index of "i2" is 2
                _index = _string[1]
                _indexPlaylist = Main.getPlaylistByIndex(_index)
                if(_indexPlaylist != None):
                    _result.append(_indexPlaylist.id)
                else:
                    printS("Failed to add playlist with index ", _index, ".", color=colors["FAIL"])
            else: # Assume input is ID if it's not, users problem. Could also check if ID in getAllIds()
                if(_string in _existingIds): 
                    _result.append(_string)
                else:
                    printS("Failed to add playlist with ID \"", _string, "\", no such entity found in database.", color=colors["FAIL"])
                            
        return _result
            
    def getPlaylistByIndex(index: int) -> Playlist:
        """
        Returns Playlist from PlaylistService.getAll() with by index starting at 0.

        Args:
            index (int): index of Playlist to get

        Returns:
            Playlist: Playlist if index is within bounds and can be fetched, else None
        """
        
        _all = PlaylistService.getAll()
        
        if(index >= 0 and index < len(_all)):
            return _all[index]
        
        return None
            
    def getQueueStreamByIndex(index: int) -> QueueStream:
        """
        Returns QueueStream from QueueStreamService.getAll() with by index starting at 0.

        Args:
            index (int): index of QueueStream to get

        Returns:
            QueueStream: QueueStream if index is within bounds and can be fetched, else None
        """
        
        _all = QueueStreamService.getAll()
        
        if(index >= 0 and index < len(_all)):
            return _all[index]
        
        return None
            
    def getStreamSourceByIndex(index: int) -> StreamSource:
        """
        Returns StreamSource from StreamSourceService.getAll() with by index starting at 0.

        Args:
            index (int): index of StreamSource to get

        Returns:
            StreamSource: StreamSource if index is within bounds and can be fetched, else None
        """
        
        _all = StreamSourceService.getAll()
        
        if(index >= 0 and index < len(_all)):
            return _all[index]
        
        return None

    def printSettings():
        """
        Print settings in .env settings/secrets file.

        Returns:
            None: None
        """

        printS("DEBUG: ", DEBUG,
        "\n", "LOCAL_STORAGE_PATH: ", LOCAL_STORAGE_PATH,
        "\n", "LOG_WATCHED: ", LOG_WATCHED,
        "\n", "DOWNLOAD_WEB_STREAMS: ", DOWNLOAD_WEB_STREAMS,
        "\n", "REMOVE_WATCHED_ON_FETCH: ", REMOVE_WATCHED_ON_FETCH,
        "\n", "PLAYED_ALWAYS_WATCHED: ", PLAYED_ALWAYS_WATCHED,
        "\n", "WATCHED_LOG_FILEPATH: ", WATCHED_LOG_FILEPATH,
        "\n", "BROWSER_BIN: ", BROWSER_BIN)

    def printHelp():
        """
        A simple console print that informs user of program arguments.

        Returns:
            None: None
        """

        print("--- Help ---")
        print("Arguments marked with ? are optional.")
        print("All arguments that triggers a function start with dash(-).")
        print("All arguments must be separated by space only.")
        print("\n")

        # General
        printS(helpFlags, ": Prints this information about input arguments.")
        printS(testFlags, ": A method of calling experimental code (when you want to test if something works).")
        # printS(testFlags, " + [args]: Details.")
        # printS("\t", testSwitches, " + [args]: Details.")

        # Playlist
        printS("TODO: details for playlist, use switches for list of streams and sources", ": Prints details about given playlist, with option for including streams and sources.")
        printS("TODO: create playlist from other playlists from e.g. Youtube", ": Creates a playlist from an existing playlist, e.g. YouTube.")
        printS(addPlaylistFlags, " [name: str] [? playWatchedStreams: bool] [? allowDuplicates: bool] [? streamSourceIds: list]: Add a playlist with name: name, playWatchedStreams: if playback should play watched streams, allowDuplicates: should playlist allow duplicate streams (only if the uri is the same), streamSourceIds: a list of sources (accepts unlimited number of IDs as long as it's positioned after other arguments).")
        printS(removePlaylistFlags, " [playlistIds or indices: list]: Removes playlists indicated.")
        printS(listPlaylistFlags, ": List playlists with indices that can be used instead of IDs in other commands.")
        printS(fetchPlaylistSourcesFlags, " [playlistIds or indices: list]: Fetch new streams from sources in playlists indicated, e.g. if a playlist has a YouTube channel as a source, and the channel uploads a new video, this video will be added to the playlist.")
        printS(prunePlaylistFlags, " [playlistIds or indices: list]: Prune playlists indicated, removeing watched streams?, streams with no parent playlist, and links to stream in playlist if the stream cannot be found in the database.")
        printS(playFlags, " [playlistId: str] [? starindex: int] [? shuffle: bool] [? repeat: bool]: Start playing stream from a playlist, order and automation (like skipping already watched streams) depending on the input and playlist.")
        # Stream
        printS(addStreamFlags, " [playlistId or index: str] TODO : Add a stream to a playlist with name: name, .")
        printS(removeStreamFlags, " [playlistId or index: str] [streamIds or indices: list]: Remove streams from playlist.")
        # Sources
        printS(listSourcesFlags, " [playlistId or index: str]: Lists sources with indices that can be used instead of IDs in other commands.")
        printS(addSourcesFlags, " [playlistId or index: str] TODO: details.")
        printS(removeSourceFlags, " [sourceId or index: str]: Removes source from database and playlist if used anywhere.")
        # Meta
        printS(listSettingsFlags, ": Lists settings currently used by program. These settings can also be found in the file named \".env\" with examples in the file \".env-example\"")

if __name__ == "__main__":
    Main.main()
