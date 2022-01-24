import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from myutil.Util import *

from FetchService import FetchService
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource
from PlaybackService import PlaybackService
from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService
from SharedService import SharedService
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

# General
helpFlags = ["-help", "-h"]
testFlags = ["-test", "-t"]
editFlags = ["-edit", "-e"]
searchFlags = ["-search", "-s"]

# Playlist
addPlaylistFlags = ["-addplaylist", "-apl", "-ap"]
addPlaylistFromYouTubeFlags = ["-addplaylistfromyoutube", "-apfy", "-fromyoutube", "-fyt", "-fy"]
deletePlaylistFlags = ["-deleteplaylist", "-dpl"]
restorePlaylistFlags = ["-restoreplaylist", "-rpl", "-rp"]
listPlaylistFlags = ["-listplaylist", "-lpl", "-lp"]
detailsPlaylistFlags = ["-detailsplaylist", "-dpl", "-dp"]
fetchPlaylistSourcesFlags = ["-fetch", "-f", "-update", "-u"]
prunePlaylistFlags = ["-prune"]
purgePlaylistFlags = ["-purge"]
resetPlaylistFetchFlags = ["-reset"]
playFlags = ["-play", "-p"]
quitSwitches = ["quit", "q", "exit", "end"]
skipSwitches = ["skip", "s"]
addCurrentToPlaylistSwitches = ["addto", "at"]
printPlaybackDetailsSwitches = ["detailsprint", "details", "print", "dp"]

# Stream
addStreamFlags = ["-add", "-a"]
deleteStreamFlags = ["-delete", "-dm", "-d"]
restorePlaylistFlags = ["-restore", "-r"]
# Sources
addSourcesFlags = ["-addsource", "-as"]
deleteSourceFlags = ["-deletesource", "-ds"]
restoreSourceFlags = ["-restoresource", "-rs"]
listSourcesFlags = ["-listsources", "-ls"]
# Meta
listSettingsFlags = ["-settings", "-secrets"]

class Main:
    fetchService = FetchService()
    playbackService = PlaybackService(quitSwitches, skipSwitches, addCurrentToPlaylistSwitches, printPlaybackDetailsSwitches)
    playlistService = PlaylistService()
    queueStreamService = QueueStreamService()
    sharedService = SharedService()
    streamSourceService = StreamSourceService()
    utility = Utility()

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
                    x = Main.queueStreamService.get("e54cde08-5c09-4558-9f4f-2bfcb062ac3f", 1)
                    print(x)
                    
                quit()            
                
            elif(arg in editFlags):
                # Expected input: playlistId or index
                _input = extractArgs(argIndex, argV)
                
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                if(len(_ids) == 0):
                    printS("Failed to edit, missing playlistId or index.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue

                filepath = os.path.join(LOCAL_STORAGE_PATH, "Playlist", _ids[0] + ".json")
                filepath = str(filepath).replace("\\", "/")
                os.startfile(filepath)
                    
                argIndex += len(_input) + 1
                continue

            elif(arg in searchFlags):
                # Expected input: searchTerm, includeSoftDeleted?
                _input = extractArgs(argIndex, argV)
                _searchTerm = _input[0] if(len(_input) > 0) else ""
                _includeSoftDeleted = eval(_input[1]) if(len(_input) > 1) else False

                _result = Main.sharedService.search(_searchTerm, _includeSoftDeleted)
                
                # _result is a dict of string keys, list values, get values from [*_result.values()]
                # list of list, for each list, for each entry, str.join id, name, and uri, then join back to list of lists of strings, ready for printLists
                _resultList = [[" - ".join([e.id, e.name, e.uri]) for e in l] for l in [*_result.values()]]
                Main.utility.printLists(_resultList, [*_result.keys()])
                    
                argIndex += len(_input) + 1
                continue
            
            # Playlist
            elif(arg in addPlaylistFlags):
                # Expected input: name, playWatchedStreams?, allowDuplicates?, streamSourceIds/indices?
                _input = extractArgs(argIndex, argV)
                _name = _input[0] if(len(_input) > 0) else "New Playlist"
                _playWatchedStreams = eval(_input[1]) if(len(_input) > 1) else None
                _allowDuplicates = eval(_input[2]) if(len(_input) > 2) else True
                _streamSourceIds = Main.getIdsFromInput(_input[3:], Main.playlistService.getAllIds(), Main.playlistService.getAll()) if(len(_input) > 3) else []

                _entity = Playlist(name = _name, playWatchedStreams = _playWatchedStreams, allowDuplicates = _allowDuplicates, streamSourceIds = _streamSourceIds)
                _result = Main.playlistService.add(_entity)
                if(_result != None):
                    printS("Playlist added successfully with ID \"", _result.id, "\".", color = colors["OKGREEN"])
                else:
                    printS("Failed to create Playlist. See rerun command with -help to see expected arguments.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in addPlaylistFromYouTubeFlags):
                # Expected input: youTubePlaylistUrl, name?, playWatchedStreams?, allowDuplicates?
                _input = extractArgs(argIndex, argV)
                _url = _input[0] if(len(_input) > 0) else None
                _name = _input[1] if(len(_input) > 1) else None
                _playWatchedStreams = eval(_input[2]) if(len(_input) > 2) else None
                _allowDuplicates = eval(_input[3]) if(len(_input) > 3) else True

                _entity = Playlist(name = _name, playWatchedStreams = _playWatchedStreams, allowDuplicates = _allowDuplicates)
                _result = Main.playlistService.addYouTubePlaylist(_entity, _url)
                if(_result != None):
                    printS("Playlist \"", _result.name, "\" added successfully from YouTube playlist.", color = colors["OKGREEN"])
                else:
                    printS("Failed to create Playlist. See rerun command with -help to see expected arguments.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in deletePlaylistFlags):
                # Expected input: playlistIds or indices
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                
                if(len(_ids) == 0):
                    printS("Failed to delete playlists, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                for _id in _ids:
                    _result = Main.playlistService.delete(_id)
                    if(_result != None):
                        printS("Playlist deleted successfully.", color = colors["OKGREEN"])
                    else:
                        printS("Failed to delete playlist. See rerun command with -help to see expected arguments.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in listPlaylistFlags):
                # Expected input: includeSoftDeleted?
                _input = extractArgs(argIndex, argV)
                _includeSoftDeleted = eval(_input[0]) if(len(_input) > 0) else False

                _result = Main.playlistService.getAll(_includeSoftDeleted)
                if(len(_result) > 0):
                    _nPlaylists = len(_result)
                    _nQueueStreams = len(Main.queueStreamService.getAll(_includeSoftDeleted))
                    _nStreamSources = len(Main.streamSourceService.getAll(_includeSoftDeleted))
                    printS(_nPlaylists, " Playlists, ", _nQueueStreams, " QueueStreams, ", _nStreamSources, " StreamSources.")
                    
                    for (i, _entry) in enumerate(_result):
                        printS(i, " - ", _entry.summaryString())
                else:
                    printS("No Playlists found.", color = colors["WARNING"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in detailsPlaylistFlags):
                # Expected input: playlistIds or indices, includeUrl, includeId
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True)
                _lenIds = len(_ids)
                _includeUri = eval(_input[_lenIds]) if(len(_input) > _lenIds) else False
                _includeId = eval(_input[_lenIds + 1]) if(len(_input) > _lenIds + 1) else False
                _includeDatetime = eval(_input[_lenIds + 2]) if(len(_input) > _lenIds + 2) else False
                _includeListCount = eval(_input[_lenIds + 3]) if(len(_input) > _lenIds + 3) else True
                
                if(len(_ids) == 0):
                    printS("Failed to print details, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _result = Main.playlistService.printPlaylistDetails(_ids, _includeUri, _includeId, _includeDatetime, _includeListCount)
                if(_result):
                    printS("Finished printing details.", color = colors["OKGREEN"])
                else:
                    printS("Failed print details.", color = colors["FAIL"])
                        
                argIndex += len(_input) + 1
                continue

            elif(arg in fetchPlaylistSourcesFlags):
                # Expected input: playlistIds or indices, fromDateTime?, toDatetime?
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True)
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
                    _result = Main.fetchService.fetch(_id, batchSize = 20, takeAfter = _takeAfter, takeBefore = _takeBefore)
                    _playlist = Main.playlistService.get(_id)
                    printS("Fetched ", _result, " for playlist \"", _playlist.name, "\" successfully.", color = colors["OKGREEN"])

                argIndex += len(_input) + 1
                continue

            elif(arg in prunePlaylistFlags):
                # Expected input: playlistIds or indices, includeSoftDeleted, permanentlyDelete, "accept changes" input within purge method
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                _lenIds = len(_ids)
                _includeSoftDeleted = eval(_input[_lenIds]) if(len(_input) > _lenIds) else False
                _permanentlyDelete = eval(_input[_lenIds + 1]) if(len(_input) > _lenIds + 1) else False
                
                if(len(_ids) == 0):
                    printS("Failed to prune playlists, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                for _id in _ids:
                    _result = Main.playlistService.prune(_id, _includeSoftDeleted, _permanentlyDelete)
                    
                    if(len(_result["QueueStream"]) > 0 and len(_result["QueueStreamId"]) > 0):
                        printS("Prune finished, deleted ", len(_result["QueueStream"]), " streams, ", len(_result["QueueStreamId"]), " IDs from playlist (ID: \"", _id, "\").", color = colors["OKGREEN"])
                    else:
                        printS("Prune failed, could not delete any streams from playlist (ID: \"", _id, "\").", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in purgePlaylistFlags):
                # Expected input: includeSoftDeleted, permanentlyDelete, "accept changes" input within purge method
                _input = extractArgs(argIndex, argV)
                _includeSoftDeleted = eval(_input[0]) if(len(_input) > 0) else False
                _permanentlyDelete = eval(_input[1]) if(len(_input) > 1) else False
                
                _result = Main.playlistService.purge(_includeSoftDeleted, _permanentlyDelete)
                if(len(_result["QueueStream"]) > 0 or len(_result["StreamSource"]) > 0 or len(_result["QueueStreamId"]) > 0 or len(_result["StreamSourceId"]) > 0):
                    printS("Purge finished, deleted ", len(_result["QueueStream"]), " QueueStreams, ", len(_result["StreamSource"]), " StreamSources, and ", len(_result["QueueStreamId"]) + len(_result["StreamSourceId"]), " IDs.", color = colors["OKGREEN"])
                else:
                    printS("Purge failed.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in resetPlaylistFetchFlags):
                # Expected input: playlistIds or indices
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                
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
                # Expected input: playlistId or index, startIndex, shuffle, repeat
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
                _startIndex = _input[1] if(len(_input) > 1) else 0
                _shuffle = eval(_input[2]) if(len(_input) > 2) else False
                _repeat = eval(_input[3]) if(len(_input) > 3) else False
                
                if(len(_ids) == 0):
                    printS("Failed to play playlist, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                if(not isNumber(_startIndex, intOnly = True)):
                    printS("Failed to play playlist, input startIndex must be an integer.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _startIndex = int(float(_startIndex))
                _result = Main.playbackService.play(_ids[0], _startIndex, _shuffle, _repeat)
                if(not _result):
                    _playlist = Main.playlistService.get(_ids[0])
                    printS("Failed to play playlist \"", _playlist.name, "\".", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            # Streams
            elif(arg in addStreamFlags):
                # Expected input: playlistId or index, uri, name?
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
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
                    _name = Main.utility.getPageTitle(_uri)
                elif(_name == None):
                    _name = "New stream"
                    printS("Could not automatically get the web name for this stream, will be named \"" , _name, "\".", color = colors["WARNING"])

                _entity = QueueStream(name = _name, uri = _uri)
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
                    # Try to delete added QueueStream if update playlist fails
                    _deleteResult = Main.queueStreamService.delete(_addResult.id)
                    _deleteMessage = "" if _deleteResult != None else " QueueStream was not deleted, ID: " + _addResult.id
                    printS("Failed to add QueueStream to playlist.", _deleteMessage, color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in deleteStreamFlags):
                # Expected input: playlistId or index, queueStreamIds or indices
                _input = extractArgs(argIndex, argV)

                _playlistIds = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
                if(len(_playlistIds) == 0):
                    printS("Failed to delete streams, missing playlistId or index.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _playlist = Main.playlistService.get(_playlistIds[0])
                _queueStreamIds = Main.utility.getIdsFromInput(_input[1:], _playlist.streamIds, Main.playlistService.getStreamsByPlaylistId(_playlist.id))
                if(len(_queueStreamIds) == 0):
                    printS("Failed to delete streams, missing queueStreamIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _result = Main.playlistService.deleteStreams(_playlist.id, _queueStreamIds)
                if(len(_result) > 0):
                    printS("deleted ", len(_result), " QueueStreams successfully from playlist \"", _playlist.name, "\".", color = colors["OKGREEN"])
                else:
                    printS("Failed to delete QueueStreams. See rerun command with -help to see expected arguments.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            # Sources
            elif(arg in addSourcesFlags):
                # Expected input: playlistId or index, uri, enableFetch?, backgroundContent?, name?
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
                _uri = _input[1] if len(_input) > 1 else None
                _enableFetch = eval(_input[2]) if len(_input) > 2 else False
                _bgContent = eval(_input[3]) if len(_input) > 3 else False
                _name = _input[4] if len(_input) > 4 else None

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
                    _name = Main.utility.getPageTitle(_uri)
                else:
                    _name = "New source"
                    printS("Could not automatically get the web name for this stream, will be named \"" , _name, "\".", color = colors["WARNING"])

                _entity = StreamSource(name = _name, uri = _uri, enableFetch = _enableFetch)
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
                    # Try to delete added StreamSource if update playlist fails
                    _deleteResult = Main.streamSourceService.delete(_addResult.id)
                    _deleteMessage = "" if _deleteResult != None else " StreamSource was not deleted, ID: " + _addResult.id
                    printS("Failed to add StreamSource to playlist.", _deleteMessage, color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in deleteSourceFlags):
                # Expected input: streamSourceIds or indices
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.streamSourceService.getAllIds(), Main.streamSourceService.getAll())
                
                if(len(_ids) == 0):
                    printS("Failed to delete source, missing streamSourceIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                for _id in _ids:
                    _result = Main.streamSourceService.delete(_id)
                    if(_result != None):
                        printS("StreamSource deleted successfully (ID ", _result.id, ").", color = colors["OKGREEN"])
                    else:
                        printS("Failed to delete StreamSource. See rerun command with -help to see expected arguments.", color = colors["FAIL"])

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
        printS(editFlags, " [playlistId or index: str]: Opens the file with Playlist.")
        printS(searchFlags, " [searchTerm: str] [? includeSoftDeleted: bool]: Search all Playlists, QueueStreams, and StreamQueues, uri and names where available. Supports Regex.")

        # Playlist
        printS(addPlaylistFlags, " [name: str] [? playWatchedStreams: bool] [? allowDuplicates: bool] [? streamSourceIds: list]: Add a Playlist with name: name, playWatchedStreams: if playback should play watched QueueStreams, allowDuplicates: should Playlist allow duplicate QueueStreams (only if the uri is the same), streamSourceIds: a list of StreamSources.")
        printS(addPlaylistFromYouTubeFlags, " [youTubePlaylistUrl: str] [? name: str] [? playWatchedStreams: bool] [? allowDuplicates: bool]: Add a Playlist and populate it with QueueStreams from given YouTube playlist youTubePlaylistUrl, with name: name, playWatchedStreams: if playback should play watched streams, allowDuplicates: should Playlist allow duplicate QueueStreams (only if the uri is the same).")
        printS(deletePlaylistFlags, " [playlistIds or indices: list]: deletes Playlists indicated.")
        # printS(restoreSourceFlags, " [playlistIds or index: str]: restore soft deleted Playlist from database.")
        printS(listPlaylistFlags, " [? includeSoftDeleted: bool]: List Playlists with indices that can be used instead of IDs in other commands.")
        printS(detailsPlaylistFlags, " [playlistIds or indices: list] [? enableFetch: bool] [? enableFetch: bool]: Prints details about given playlist, with option for including StreamSources and QueueStreams.")
        printS(fetchPlaylistSourcesFlags, " [playlistIds or indices: list] [? takeAfter: datetime] [? takeBefore: datetime]: Fetch new streams from StreamSources in Playlists indicated, e.g. if a Playlist has a YouTube channel as a source, and the channel uploads a new video, this video will be added to the Playlist. Optional arguments takeAfter: only fetch QueueStreams after this date, takeBefore: only fetch QueueStreams before this date. Dates formatted like \"2022-01-30\" (YYYY-MM-DD)")
        printS(prunePlaylistFlags, " [playlistIds or indices: list]: Prune Playlists indicated, deleteing watched QueueStreams.")
        printS(purgePlaylistFlags, " [? includeSoftDeleted: bool] [? permanentlyDelete: bool]: Purge database indicated, removing IDs with no corresponding relation and deleteing StreamSources and QueueStreams with no linked IDs in Playlists.")
        printS(resetPlaylistFetchFlags, " [playlistIds or indices: list]: Resets fetch status of StreamSources in a Playlist and deletes QueueStreams from Playlist.")
        printS(playFlags, " [playlistId: str] [? starindex: int] [? shuffle: bool] [? repeat: bool]: Start playing stream from a Playlist, order and automation (like skipping already watched QueueStreams) depending on the input and Playlist.")
        printS("\t", quitSwitches, ": End current playback and contintue the program without playing anymore QueueStreams in Playlist. Only available while Playlist is playing.")
        printS("\t", skipSwitches, ": Skip current QueueStream playing. This QueueStream will not be marked as watched. Only available while Playlist is playing.")
        printS("\t", addCurrentToPlaylistSwitches, " [playlistId or index: str]: Add the current QueueStream to another Playlist indicated by ID on index. Only available while Playlist is playing.")
        printS("\t", printPlaybackDetailsSwitches, ": Prints details of current playing Playlist,")

        # Stream
        printS(addStreamFlags, " [playlistId or index: str] [uri: string] [? name: str]: Add a stream to a Playlist from ID or index, from uri: URL, and name: name (set automatically if not given).")
        printS(deleteStreamFlags, " [streamIds or indices: list]: delete QueueStreams from Playlist.")
        # printS(restoreSourceFlags, " [streamIds or index: str]: restore soft deleted QueueStreams from database.")
        # Sources
        printS(addSourcesFlags, " [playlistId or index: str] [uri: string] [? enableFetch: bool] [? name: str]: Add a StreamSources from uri: URL, enableFetch: if the Playlist should fetch new stream from this StreamSource, and name: name (set automatically if not given).")
        # printS(addSourcesFlags, " [playlistId or index: str] [uri: string] [? enableFetch: bool] [? backgroundContent: bool] [? name: str]: Add a StreamSources from uri: URL, enableFetch: if the Playlist should fetch new QueueStream from this StreamSource, backgroundContent; if the QueueStream from this source are things you would play in the background, and name: name (set automatically if not given).")
        printS(deleteSourceFlags, " [sourceIds or index: str]: deletes StreamSources from database and Playlist if used anywhere.")
        # printS(restoreSourceFlags, " [sourceId or index: str]: restore soft deleted StreamSources from database.")
        printS(listSourcesFlags, " [playlistId or index: str]: Lists StreamSources with indices that can be used instead of IDs in other commands.")
        # Meta
        printS(listSettingsFlags, ": Lists settings currently used by program. These settings can also be found in the file named \".env\" with examples in the file \".env-example\"")

if __name__ == "__main__":
    Main.main()
