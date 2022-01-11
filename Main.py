from datetime import datetime
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
detailsPlaylistFlags = ["-detailsplaylist", "-dpl", "-dp"]
fetchPlaylistSourcesFlags = ["-fetch", "-f", "-update", "-u"]
prunePlaylistFlags = ["-prune", "-pr"]
resetPlaylistFetchFlags = ["-reset"]
playFlags = ["-play", "-p"]
quitSwitches = ["quit", "q", "exit", "end"]
skipSwitches = ["skip", "s"]
addCurrentToPlaylistSwitches = ["addto", "at"]

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
    playlistService = PlaylistService(quitSwitches, skipSwitches, addCurrentToPlaylistSwitches)
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
                argIndex += 1
                continue

            elif(arg in testFlags):
                _input = extractArgs(argIndex, argV)
                printS("Test", color = colors["OKBLUE"])

                if(1):
                    printS("testing code here")
                    
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
                    printS("Playlist added successfully with ID \"", _result.id, "\".", color = colors["OKGREEN"])
                else:
                    printS("Failed to create Playlist. See rerun command with -help to see expected arguments.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in removePlaylistFlags):
                # Expected input: playlistIds or indices
                _input = extractArgs(argIndex, argV)
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                
                if(len(_ids) == 0):
                    printS("Failed to remove playlists, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                for _id in _ids:
                    _result = Main.playlistService.remove(_id)
                    if(_result != None):
                        printS("Playlist removed successfully.", color = colors["OKGREEN"])
                    else:
                        printS("Failed to remove playlist. See rerun command with -help to see expected arguments.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in listPlaylistFlags):
                # Expected input: None

                _result = Main.playlistService.getAll()
                if(len(_result) > 0):
                    for (i, _entry) in enumerate(_result):
                        printS(i, " - ", _entry.summaryString())
                else:
                    printS("No Playlists found.", color = colors["WARNING"])

                argIndex += 1
                continue
            
            elif(arg in detailsPlaylistFlags):
                # Expected input: playlistIds or indices, includeUrl, includeId
                _input = extractArgs(argIndex, argV)
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True)
                _lenIds = len(_ids)
                _includeUri = eval(_input[_lenIds]) if(len(_input) > _lenIds) else False
                _includeId = eval(_input[_lenIds + 1]) if(len(_input) > _lenIds + 1) else False
                _includeDatetime = eval(_input[_lenIds + 2]) if(len(_input) > _lenIds + 2) else False
                _includeListCount = eval(_input[_lenIds + 3]) if(len(_input) > _lenIds + 3) else False
                
                if(len(_ids) == 0):
                    printS("Failed to print details, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _result = Main.printPlaylistDetails(_ids, _includeUri, _includeId, _includeDatetime, _includeListCount)
                if(_result):
                    printS("Finished printing details.", color = colors["OKGREEN"])
                else:
                    printS("Failed print details.", color = colors["FAIL"])
                        
                argIndex += len(_input) + 1
                continue

            elif(arg in fetchPlaylistSourcesFlags):
                # Expected input: playlistIds or indices, fromDateTime?, toDatetime?
                _input = extractArgs(argIndex, argV)
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True)
                _lenIds = len(_ids)
                _takeAfter = _input[_lenIds] if(len(_input) > _lenIds) else None
                _takeBefore = _input[_lenIds + 1] if(len(_input) > _lenIds + 1) else None
                
                if(len(_ids) == 0):
                    printS("Failed to fetch sources, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                try:
                    if(_takeAfter != None):
                        _takeAfter = datetime.strptime(_takeAfter, "%Y-%m-%d")
                    if(_takeBefore != None):
                        _takeBefore = datetime.strptime(_takeBefore, "%Y-%m-%d")
                except:
                    printS("Dates for takeAfter and takeBefore were not valid, see -help print for format.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                for _id in _ids:
                    _result = Main.fetchService.fetch(_id, takeAfter = _takeAfter, takeBefore = _takeBefore)
                    _playlist = Main.playlistService.get(_id)
                    printS("Fetched ", _result, " for playlist \"", _playlist.name, "\" successfully.", color = colors["OKGREEN"])

                argIndex += len(_input) + 1
                continue

            elif(arg in prunePlaylistFlags):
                # Expected input: playlistIds or indices
                _input = extractArgs(argIndex, argV)
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                
                if(len(_ids) == 0):
                    printS("Failed to prune playlists, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                for _id in _ids:
                    _result = Main.playlistService.prune(_id)
                    
                    if(len(_result) > 0):
                        printS("Prune finished, removed ", len(_result), " streams from playlist (ID: \"", _id, "\").", color = colors["OKGREEN"])
                    else:
                        printS("Prune finished, could not remove any streams from playlist (ID: \"", _id, "\").", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in resetPlaylistFetchFlags):
                # Expected input: playlistIds or indices
                _input = extractArgs(argIndex, argV)
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                
                if(len(_ids) == 0):
                    printS("Failed to reset fetch-status of playlists, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                    
                _result = Main.resetPlaylistFetch(_ids)
                if(_result):
                    printS("Finished resetting fetch statuses for sources in playlists.", color = colors["OKGREEN"])
                else:
                    printS("Failed to reset fetch statuses for sources in playlists.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in playFlags):
                # Expected input: playlistId or index
                _input = extractArgs(argIndex, argV)
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                
                if(len(_ids) == 0):
                    printS("Failed to prune playlists, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue

                _result = Main.playlistService.playCmd(_ids[0])
                if(not _result):
                    _playlist = Main.playlistService.get(_ids[0])
                    printS("Failed to play playlist \"", _playlist.name, "\", please se error above.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            # Streams
            elif(arg in addStreamFlags):
                # Expected input: playlistId or index, uri, name?
                _input = extractArgs(argIndex, argV)
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
                _uri = _input[1] if len(_input) > 1 else None
                _name = _input[2] if len(_input) > 2 else None

                if(len(_ids) == 0):
                    printS("Failed to add QueueStream, missing playlistId or index.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue

                if(_uri == None):
                    printS("Failed to add QueueStream, missing uri.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue

                if(_name == None and validators.url(_uri)):
                    _name = Main.fetchService.getPageTitle(_uri)
                elif(_name == None):
                    _name = "New stream"
                    printS("Could not automatically get the web name for this stream, will be named \"" , _name, "\".", color = colors["WARNING"])

                _entity = QueueStream(name=_name, uri=_uri)
                _addResult = Main.queueStreamService.add(_entity)
                if(_addResult == None):
                    printS("Failed to create QueueStream.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                    
                _playlist = Main.playlistService.get(_ids[0])
                _playlist.streamIds.append(_addResult.id)
                _updateResult = Main.playlistService.update(_playlist)
                if(_updateResult != None):
                    printS("QueueStream added successfully with ID \"", _addResult.id, "\".", color = colors["OKGREEN"])
                else:
                    # Try to remove added QueueStream if update playlist fails
                    _removeResult = Main.queueStreamService.remove(_addResult.id)
                    _removeMessage = "" if _removeResult != None else " QueueStream was not removed, ID: " + _addResult.id
                    printS("Failed to add QueueStream to playlist.", _removeMessage, color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in removeStreamFlags):
                # Expected input: playlistId or index, queueStreamIds or indices
                _input = extractArgs(argIndex, argV)

                _playlistIds = Main.getIdsFromInput(_input, Main.queueStreamService.getAllIds(), Main.queueStreamService.getAll(), 1)
                if(len(_playlistIds) == 0):
                    printS("Failed to remove streams, missing playlistId or index.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _queueStreamIds = Main.getIdsFromInput(_input[1:], Main.queueStreamService.getAllIds(), Main.queueStreamService.getAll())
                if(len(_queueStreamIds) == 0):
                    printS("Failed to remove streams, missing queueStreamIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _playlist = Main.playlistService.get(_playlistIds[0])
                # TODO should be ids, not indicies
                printS("WIP", color = colors["OKGREEN"])
                quit()
                _result = Main.playlistService.removeStreams(_playlist.id, _queueStreamIds)
                if(len(_result) > 0):
                    printS("Removed ", len(_result), " QueueStreams successfully from playlist \"", _playlist.name, "\".", color = colors["OKGREEN"])
                else:
                    printS("Failed to remove QueueStreams. See rerun command with -help to see expected arguments.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            # Sources
            elif(arg in addSourcesFlags):
                # Expected input: playlistId or index, uri, enableFetch?, name?
                _input = extractArgs(argIndex, argV)
                _ids = Main.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
                _uri = _input[1] if len(_input) > 1 else None
                _enableFetch = eval(_input[2]) if len(_input) > 2 else False
                _name = _input[3] if len(_input) > 3 else None

                if(len(_ids) == 0):
                    printS("Failed to add StreamSource, missing playlistId or index.", color = colors["FAIL"])
                    if(DEBUG): printS("IDs: ", _ids, color = colors["WARNING"])
                    argIndex += len(_input) + 1
                    continue

                if(_uri == None):
                    printS("Failed to add StreamSource, missing uri.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue

                if(_name == None):
                    _name = Main.fetchService.getPageTitle(_uri)
                else:
                    _name = "New source"
                    printS("Could not automatically get the web name for this stream, will be named \"" , _name, "\".", color = colors["WARNING"])

                _entity = StreamSource(name=_name, uri = _uri, enableFetch = _enableFetch)
                _addResult = Main.streamSourceService.add(_entity)
                if(_addResult == None):
                    printS("Failed to create StreamSource.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _playlist = Main.playlistService.get(_ids[0])
                _playlist.streamSourceIds.append(_addResult.id)
                _updateResult = Main.playlistService.update(_playlist)
                if(_updateResult != None):
                    printS("StreamSource added successfully with ID \"", _addResult.id, "\".", color = colors["OKGREEN"])
                else:
                    # Try to remove added StreamSource if update playlist fails
                    _removeResult = Main.streamSourceService.remove(_addResult.id)
                    _removeMessage = "" if _removeResult != None else " StreamSource was not removed, ID: " + _addResult.id
                    printS("Failed to add StreamSource to playlist.", _removeMessage, color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in removeSourceFlags):
                # Expected input: streamSourceIds or indices
                _input = extractArgs(argIndex, argV)
                _ids = Main.getIdsFromInput(_input, Main.streamSourceService.getAllIds(), Main.streamSourceService.getAll())
                
                if(len(_ids) == 0):
                    printS("Failed to remove source, missing streamSourceIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                for _id in _ids:
                    _result = Main.streamSourceService.remove(_id)
                    if(_result != None):
                        printS("StreamSource removed successfully (ID ", _result.id, ").", color = colors["OKGREEN"])
                    else:
                        printS("Failed to remove StreamSource. See rerun command with -help to see expected arguments.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in listSourcesFlags):
                # Expected input: None

                _result = Main.streamSourceService.getAll()
                if(len(_result) > 0):
                    for (i, _entry) in enumerate(_result):
                        printS(i, " - ", _entry.summaryString())
                else:
                    printS("No QueueStreams found.", color = colors["WARNING"])

                argIndex += 1
                continue

            # Settings
            elif(arg in listSettingsFlags):
                Main.printSettings()

                argIndex += 1
                continue

            # Invalid
            else:
                printS("Argument not recognized: \"", arg, "\", please see documentation or run with \"-help\" for help.", color = colors["WARNING"])
                argIndex += 1

    def getIdsFromInput(input: List[str], existingIds: List[str], indexList: List[any], limit: int = None, returnOnNonIds: bool = False) -> List[str]:
        """
        Get IDs from a list of inputs, whether they are raw IDs that must be checked via the database or indices (formatted "i[index]") of a list.

        Args:
            input (List[str]): input if IDs/indices
            existingIds (List[str]): existing IDs to compare with
            indexList (List[any]): List of object (must have field "id") to index from
            limit (int): limit the numbers of arguments to parse
            returnOnNonIds (bool): return valid input IDs if the current input is no an ID, to allow input from user to be something like \"id id id bool\" which allows unspecified IDs before other arguments 

        Returns:
            List[str]: List of existing IDs for input which can be found
        """
        
        if(len(existingIds) == 0 or len(indexList) == 0):
            if(DEBUG): printS("Length of input \"existingIds\" (", len(existingIds), ") or \"indexList\" (", len(indexList), ") was 0.", color = colors["WARNING"])
            return []

        _result = []
        for i, _string in enumerate(input):
            if(limit != None and i >= limit):
                if(DEBUG): printS("Returning data before input ", _string, ", limit (", limit, ") reached.", color = colors["WARNING"])
                break
            
            if(_string[0] == "i"):  # starts with "i", like index of "i2" is 2
                if(not isNumber(_string[1])):
                    if(returnOnNonIds):
                        return _result
                    
                    printS("Argument ", _string, " is not a valid index format, must be \"i\" followed by an integer, like \"i0\". Argument not processed.", color = colors["FAIL"])
                    continue

                _index = int(float(_string[1]))
                _indexedEntity = indexList[_index]

                if(_indexedEntity != None):
                    _result.append(_indexedEntity.id)
                else:
                    if(returnOnNonIds):
                        return _result
                    
                    printS("Failed to get data for index ", _index, ", it is out of bounds.", color = colors["FAIL"])
            else:  # Assume input is ID if it's not, users problem. Could also check if ID in getAllIds()
                if(_string in existingIds):
                    _result.append(_string)
                else:
                    if(returnOnNonIds):
                        return _result
                    
                    printS("Failed to add playlist with ID \"", _string, "\", no such entity found in database.", color = colors["FAIL"])
                    continue

        return _result

    def printPlaylistDetails(playlistIds: List[str], includeUri: bool = False, includeId: bool = False, includeDatetime: bool = False, includeListCount: bool = False) -> int:
        """
        Print detailed info for Playlist, including details for related StreamSources and QueueStreams.

        Args:
            playlistIds (List[str]): list of playlistIds to print details of
            includeUri (bool, optional): should print include URI if any. Defaults to False
            includeId (bool, optional): should print include IDs. Defaults to False
            
        Returns:
            int: number of playlists printed for
        """
        
        _result = 0
        for _id in playlistIds:
            _playlist = Main.playlistService.get(_id)
              
            _playlistDetailsString = _playlist.detailsString(includeUri, includeId, includeDatetime, includeListCount = False)
            if(includeListCount):
                _unwatchedStreams = Main.playlistService.getUnwatchedStreamsByPlaylistId(_playlist.id)
                _fetchedSources = Main.playlistService.getFetchedSourcesByPlaylistId(_playlist.id)
                _sourcesListString = ", n streamIds: " + str(len(_playlist.streamIds)) + ", unwatched streamIds: " + str(len(_unwatchedStreams))
                _streamsListString = ", n streamSourceIds: " + str(len(_playlist.streamSourceIds)) + ", fetched streamSourceIds: " + str(len(_fetchedSources))
                _playlistDetailsString += _sourcesListString + _streamsListString
                            
            printS(_playlistDetailsString)
            
            printS("\tStreamSources", color = colors["BOLD"])
            for i, _sourceId in enumerate(_playlist.streamSourceIds):
                _source = Main.streamSourceService.get(_sourceId)
                if(_source == None):
                    printS("\\tSource not found (ID: \"", _sourceId, "\").", color = colors["FAIL"])
                    continue
                
                _color = "WHITE" if i % 2 == 0 else "GREYBG"
                printS("\t", str(i), " - ", _source.detailsString(includeUri, includeId, includeDatetime, includeListCount), color = colors[_color])
            
            print("\n")
            printS("\tQueueStreams", color = colors["BOLD"])
            for i, _streamId in enumerate(_playlist.streamIds):
                _stream = Main.queueStreamService.get(_streamId)
                if(_stream == None):
                    printS("\tStream not found (ID: \"", _streamId, "\").", color = colors["FAIL"])
                    continue
                
                _color = "WHITE" if i % 2 == 0 else "GREYBG"
                printS("\t", str(i), " - ", _stream.detailsString(includeUri, includeId, includeDatetime, includeListCount), color = colors[_color])
                
            _result += 1
                
        return _result
    
    def resetPlaylistFetch(playlistIds: List[str]) -> int:
        """
        Reset the fetch-status for sources of a playlist and removes all streams.

        Args:
            playlistIds (List[str]): list of playlistIds 
            
        Returns:
            int: number of playlists reset
        """
        
        _result = 0
        for playlistId in playlistIds:            
            _playlist = Main.playlistService.get(playlistId)
            _removeUpdateResult = True
            
            for queueStreamId in _playlist.streamIds:
                _removeStreamResult = Main.queueStreamService.remove(queueStreamId)
                _removeUpdateResult = _removeUpdateResult and _removeStreamResult != None
            
            _playlist.streamIds = []
            _updateplaylistResult = Main.playlistService.update(_playlist)
            _removeUpdateResult = _removeUpdateResult and _updateplaylistResult != None
            
            for streamSourceId in _playlist.streamSourceIds:
                _streamSource = Main.streamSourceService.get(streamSourceId)
                _streamSource.lastFetched = None
                _updateStreamResult = Main.streamSourceService.update(_streamSource)
                _removeUpdateResult = _removeUpdateResult and _updateStreamResult != None
            
            if(_removeUpdateResult):
                _result += 1
                
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

        # Playlist
        printS(addPlaylistFlags, " [name: str] [? playWatchedStreams: bool] [? allowDuplicates: bool] [? streamSourceIds: list]: Add a playlist with name: name, playWatchedStreams: if playback should play watched streams, allowDuplicates: should playlist allow duplicate streams (only if the uri is the same), streamSourceIds: a list of sources.")
        printS(removePlaylistFlags, " [playlistIds or indices: list]: Removes playlists indicated.")
        printS(listPlaylistFlags, ": List playlists with indices that can be used instead of IDs in other commands.")
        printS(detailsPlaylistFlags, " [playlistIds or indices: list] [? enableFetch: bool] [? enableFetch: bool]: Prints details about given playlist, with option for including streams and sources.")
        printS(fetchPlaylistSourcesFlags, " [playlistIds or indices: list] [? takeAfter: datetime] [? takeBefore: datetime]: Fetch new streams from sources in playlists indicated, e.g. if a playlist has a YouTube channel as a source, and the channel uploads a new video, this video will be added to the playlist. Optional arguments takeAfter: only fetch streams after this date, takeBefore: only fetch streams before this date. Dates formatted like \"2022-01-30\" (YYYY-MM-DD)")
        # printS(TODO, ": Create playlist from other playlists from e.g. Youtube", ": Creates a playlist from an existing playlist, e.g. YouTube.")
        # printS(prunePlaylistFlags, " [playlistIds or indices: list]: Prune playlists indicated, removeing watched streams?, streams with no parent playlist, and links to stream in playlist if the stream cannot be found in the database.")
        printS(resetPlaylistFetchFlags, " [playlistIds or indices: list]: Resets fetch status of sources in a playlist and removes streams from playlist.")
        printS(playFlags, " [playlistId: str] [? starindex: int] [? shuffle: bool] [? repeat: bool]: Start playing stream from a playlist, order and automation (like skipping already watched streams) depending on the input and playlist.")
        printS("\t", quitSwitches, ": End current playback and contintue the program without playing anymore streams in playlist. Only available while playlist is playing.")
        printS("\t", skipSwitches, ": Skip current stream playing. This stream will not be marked as watched. Only available while playlist is playing.")
        printS("\t", addCurrentToPlaylistSwitches, " [playlistId or index: str]: Add the current stream to another playlist indicated by ID on index. Only available while playlist is playing.")

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
