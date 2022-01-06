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
addSourcesFlags = ["-addsource", "-as"]
removeSourceFlags = ["-removesource", "-rms", "-rs"]
listSourcesFlags = ["-listsources", "-ls"]
# Meta
listSettingsFlags = ["-settings", "-secrets", "-s"]

class Main:
    fetchService = FetchService()
    playlistService = PlaylistService()
    queueStreamService = QueueStreamService()
    streamSourceService = StreamSourceService()
        
    def main():
        argC = len(sys.argv)
        argV = sys.argv
        argIndex = 1

        if(argC < 2):
            Main.printHelp()

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
                    print(Main.fetchService.fetch(playlistId))
                    # print(playlistService.playCmd(playlistId))
                    
                quit()

            # Playlist
            elif(arg in addPlaylistFlags):
                # Expected input: name, playWatchedStreams?, allowDuplicates?, streamSourceIds/indices?
                _input = extractArgs(argIndex, argV)
                _name = str(_input[0]) if len(_input) > 0 else "New Playlist"
                _playWatchedStreams = eval(_input[1]) if len(_input) > 1 else True
                _allowDuplicates = eval(_input[2]) if len(_input) > 2 else True
                _streamSourceIds = Main.getIdsFromInput(_input[3:], Main.playlistService.getAllIds(), Main.playlistService.getAll()) if len(_input) > 3 else []
                
                _entity = Playlist(name = _name, playWatchedStreams = _playWatchedStreams, allowDuplicates = _allowDuplicates, streamSourceIds = _streamSourceIds)
                _result = Main.playlistService.add(_entity)
                if(_result != None):
                    printS("Playlist added successfully with ID \"", _result.id, "\".", color=colors["OKGREEN"])
                else:
                    printS("Failed to create Playlist. See rerun command with -help to see expected arguments.", color=colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in removePlaylistFlags):
                # Expected input: playlistIds or indices
                _input = extractArgs(argIndex, argV)
                if(len(_input) == 0):
                    printS("Missing options for argument \"", arg, "\", expected IDs or indices.", color=colors["WARNING"])
                    argIndex += 1
                    continue
                
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                for _id in _ids:
                    _result = Main.playlistService.remove(_id)
                    if(_result != None):
                        printS("Playlist removed successfully.", color=colors["OKGREEN"])
                    else:
                        printS("Failed to remove playlist. See rerun command with -help to see expected arguments.", color=colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in listPlaylistFlags):
                # Expected input: None

                _result = Main.playlistService.getAll()
                if(len(_result) > 0):
                    for (i, _entry) in enumerate(_result):
                        printS(i, " - ", _entry.summaryString())
                else:
                    printS("No Playlists found.", color=colors["WARNING"])

                argIndex += 1
                continue

            elif(arg in fetchPlaylistSourcesFlags):
                # Expected input: playlistIds or indices
                _input = extractArgs(argIndex, argV)
                if(len(_input) == 0):
                    printS("Missing options for argument \"", arg, "\", expected IDs or indices.", color=colors["WARNING"])
                    argIndex += 1
                    continue
                
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                for _id in _ids:
                    _result = Main.fetchService.fetch(_id)
                    _playlist = Main.playlistService.get(_id)
                    printS("Fetched ", _result, " for playlist \"", _playlist.name, "\" successfully.", color=colors["OKGREEN"])
                
                argIndex += len(_input) + 1
                continue

            elif(arg in prunePlaylistFlags):
                # Expected input: pruneoptions?, playlistIds or indices
                _input = extractArgs(argIndex, argV)
                if(len(_input) == 0):
                    printS("Missing options for argument \"", arg, "\", expected IDs or indices.", color=colors["WARNING"])
                    argIndex += 1
                    continue
                
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                for _id in _ids:
                    printS("WIP")
                
                argIndex += len(_input) + 1
                continue

            elif(arg in playFlags):
                # Expected input: playlistId or index
                _input = extractArgs(argIndex, argV)
                if(len(_input) == 0):
                    printS("Missing options for argument \"", arg, "\", expected IDs or indices.", color=colors["WARNING"])
                    argIndex += 1
                    continue
                
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())[0]
                if(len(_ids) < 1):
                    printS("Failed to play playlist \"", _playlist.name, "\", no such ID or index: \"", _input[0], "\".", color=colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _result = Main.playlistService.playCmd(_ids[0])
                if(not _result):
                    _playlist = Main.playlistService.get(_id)
                    printS("Failed to play playlist \"", _playlist.name, "\", please se error above.", color=colors["FAIL"])
                    
                argIndex += len(_input) + 1
                continue

            # Streams
            elif(arg in addStreamFlags):
                # Expected input: playlistId or index, uri, name?
                _input = extractArgs(argIndex, argV)
                _ids = Main.getIdsFromInput(_input, Main.queueStreamService.getAllIds(), Main.queueStreamService.getAll())
                _uri = _input[1] if len(_input) > 1 else None
                _name = _input[2] if len(_input) > 2 else None
                
                if(len(_ids) == 0):
                    printS("Failed to add QueueStream, missing ID to playlist.", color=colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                if(_uri == None):
                    printS("Failed to add QueueStream, missing uri.", color=colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                 # TODO if name is none, try to get filename if dir, else try to get page title if web
                if(_name == None):
                    _name = "New QueueStream"
                
                _entity = QueueStream(name = _name, uri = _uri)
                _addResult = Main.queueStreamService.add(_entity)
                if(_addResult == None):
                    printS("Failed to create QueueStream.", color=colors["FAIL"])
                
                _playlist = Main.playlistService.get(_ids[0])
                _playlist.streamIds.append(_addResult.id)
                _updateResult = Main.playlistService.update(_entity)
                if(_updateResult != None):
                    printS("QueueStream added successfully with ID \"", _result.id, "\".", color=colors["OKGREEN"])
                else:
                    _removeResult = Main.queueStreamService.remove(_addResult.id) # Try to remove added QueueStream if update playlist fails
                    _removeMessage = "" if _removeResult != None else " QueueStream was not removed, ID: " + _addResult.id
                    printS("Failed to add QueueStream to playlist.", _removeMessage, color=colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in removeStreamFlags):
                # Expected input: queueStreamIds or indices
                _input = extractArgs(argIndex, argV)
                if(len(_input) == 0):
                    printS("Missing options for argument \"", arg, "\", expected IDs or indices.", color=colors["WARNING"])
                    argIndex += 1
                    continue
                
                _ids = Main.getIdsFromInput(_input, Main.queueStreamService.getAllIds(), Main.queueStreamService.getAll())
                for _id in _ids:
                    _result = Main.queueStreamService.remove(_id)
                    if(_result != None):
                        printS("QueueStream removed successfully.", color=colors["OKGREEN"])
                    else:
                        printS("Failed to remove QueueStream. See rerun command with -help to see expected arguments.", color=colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            # Sources
            elif(arg in addSourcesFlags):
                # Expected input: uri, enableFetch?, name?
                _input = extractArgs(argIndex, argV)
                _uri = _input[0] if len(_input) > 0 else None
                _enableFetch = eval(_input[1]) if len(_input) > 1 else False
                _name = _input[2] if len(_input) > 2 else None
                
                if(_uri == None):
                    printS("Failed to add StreamSource, missing uri.", color=colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                 # TODO if name is none, try to get dirname if dir, else try to get page title if web
                if(_name == None):
                    _name = "New source"
                
                _entity = StreamSource(name = _name, uri = _uri, enableFetch = _enableFetch)
                _result = Main.streamSourceService.add(_entity)
                if(_result != None):
                    printS("StreamSource added successfully with ID \"", _result.id, "\".", color=colors["OKGREEN"])
                else:
                    printS("Failed to create StreamSource. See rerun command with -help to see expected arguments.", color=colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in removeSourceFlags):
                # Expected input: streamSourceIds or indices
                _input = extractArgs(argIndex, argV)
                if(len(_input) == 0):
                    printS("Missing options for argument \"", arg, "\", expected IDs or indices.", color=colors["WARNING"])
                    argIndex += 1
                    continue
                
                _ids = Main.getIdsFromInput(_input, Main.streamSourceService.getAllIds(), Main.streamSourceService.getAll())
                for _id in _ids:
                    _result = Main.streamSourceService.remove(_id)
                    if(_result != None):
                        printS("StreamSource removed successfully.", color=colors["OKGREEN"])
                    else:
                        printS("Failed to remove StreamSource. See rerun command with -help to see expected arguments.", color=colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in listSourcesFlags):
                # Expected input: None

                _result = Main.queueStreamService.getAll()
                if(len(_result) > 0):
                    for (i, _entry) in enumerate(_result):
                        printS(i, " - ", _entry.summaryString())
                else:
                    printS("No QueueStreams found.", color=colors["WARNING"])

                argIndex += 1
                continue
            
            # Settings
            elif(arg in listSettingsFlags):
                Main.printSettings()

                argIndex += 1
                continue

            # Invalid
            else:
                printS("Argument not recognized: \"", arg, "\", please see documentation or run with \"-help\" for help.", color=colors["WARNING"])
                argIndex += 1
            
    def getIdsFromInput(input: List[str], existingIds: List[str], indexList: List[any]) -> List[str]:
        """
        Get IDs from a list of inputs, whether they are raw IDs that must be checked via the database or indices (formatted "i[index]") of a list.

        Args:
            input (List[str]): input if IDs/indices
            existingIds (List[str]): existing IDs to compare with
            indexList (List[any]): List of object (must have field "id") to index from

        Returns:
            List[str]: List of existing IDs for input which can be found
        """
        
        _result = []
        for _string in input:
            if(_string[0] == "i"): #starts with "i", like index of "i2" is 2
                if(not isNumber(_string[1])):
                    printS("Argument ", _string, " is not a valid index format, must be \"i\" followed by an integer, like \"i0\". Argument not processed.", color=colors["FAIL"])
                    continue
                
                _index = int(float(_string[1]))
                _indexedEntity = indexList[_index] if(len(indexList) > 0 and _index > 0 and _index < len(indexList)) else None
                
                if(_indexedEntity != None):
                    _result.append(_indexedEntity.id)
                else:
                    printS("Failed to get data for index ", _index, ", it is out of bounds.", color=colors["FAIL"])
            else: # Assume input is ID if it's not, users problem. Could also check if ID in getAllIds()
                if(_string in existingIds): 
                    _result.append(_string)
                else:
                    printS("Failed to add playlist with ID \"", _string, "\", no such entity found in database.", color=colors["FAIL"])
                            
        return _result
    
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
        print("When using an index or indices, format with with an \"i\" followed by the index, like \"i0\".")
        print("\n")

        # General
        printS(helpFlags, ": Prints this information about input arguments.")
        printS(testFlags, ": A method of calling experimental code (when you want to test if something works).")
        # printS(testFlags, " + [args]: Details.")
        # printS("\t", testSwitches, " + [args]: Details.")

        # Playlist        
        printS(addPlaylistFlags, " [name: str] [? playWatchedStreams: bool] [? allowDuplicates: bool] [? streamSourceIds: list]: Add a playlist with name: name, playWatchedStreams: if playback should play watched streams, allowDuplicates: should playlist allow duplicate streams (only if the uri is the same), streamSourceIds: a list of sources.")
        printS(removePlaylistFlags, " [playlistIds or indices: list]: Removes playlists indicated.")
        printS(listPlaylistFlags, ": List playlists with indices that can be used instead of IDs in other commands.")
        printS(fetchPlaylistSourcesFlags, " [playlistIds or indices: list]: Fetch new streams from sources in playlists indicated, e.g. if a playlist has a YouTube channel as a source, and the channel uploads a new video, this video will be added to the playlist.")
        printS(prunePlaylistFlags, " [playlistIds or indices: list]: Prune playlists indicated, removeing watched streams?, streams with no parent playlist, and links to stream in playlist if the stream cannot be found in the database.")
        printS(playFlags, " [playlistId: str] [? starindex: int] [? shuffle: bool] [? repeat: bool]: Start playing stream from a playlist, order and automation (like skipping already watched streams) depending on the input and playlist.")
        
        # printS("TODO: details for playlist, use switches for list of streams and sources", ": Prints details about given playlist, with option for including streams and sources.")
        # printS("TODO: create playlist from other playlists from e.g. Youtube", ": Creates a playlist from an existing playlist, e.g. YouTube.")
        
        # Stream
        printS(addStreamFlags, " [playlistId or index: str] [uri: string] [? name: str]: Add a stream to a playlist from ID or index, from uri: URL, and name: name (set automatically if not given).")
        printS(removeStreamFlags, " [streamIds or indices: list]: Remove streams from playlist.")
        # Sources
        printS(addSourcesFlags, " [playlistId or index: str] [uri: string] [? enableFetch: bool] [? name: str]: Add a source from uri: URL, enableFetch: if the playlist should fetch new stream from this source, and name: name (set automatically if not given).")
        printS(removeSourceFlags, " [sourceId or index: str]: Removes source from database and playlist if used anywhere.")
        printS(listSourcesFlags, " [playlistId or index: str]: Lists sources with indices that can be used instead of IDs in other commands.")
        # Meta
        printS(listSettingsFlags, ": Lists settings currently used by program. These settings can also be found in the file named \".env\" with examples in the file \".env-example\"")

if __name__ == "__main__":
    Main.main()
