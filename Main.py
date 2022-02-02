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
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")

class Main:
    fetchService = FetchService()
    playbackService = PlaybackService()
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
            _help = Main.utility.getHelpString()
            printS(_help)

        makeFiles(WATCHED_LOG_FILEPATH)

        while argIndex < argC:
            arg = sys.argv[argIndex].lower()

            if(arg in Main.utility.helpCommands):
                _help = Main.utility.getHelpString()
                printS(_help)
                
                argIndex += 1
                continue

            elif(arg in Main.utility.testCommands):
                _input = extractArgs(argIndex, argV)
                printS("Test", color = colors["OKBLUE"])
                
                quit()            
                
            elif(arg in Main.utility.editCommands):
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

            elif(arg in Main.utility.searchCommands):
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
            elif(arg in Main.utility.addPlaylistCommands):
                # Expected input: name, playWatchedStreams?, allowDuplicates?, streamSourceIds/indices?
                _input = extractArgs(argIndex, argV)
                _name = _input[0] if(len(_input) > 0) else "New Playlist"
                _playWatchedStreams = eval(_input[1]) if(len(_input) > 1) else None
                _allowDuplicates = eval(_input[2]) if(len(_input) > 2) else True
                _streamSourceIds = Main.getIdsFromInput(_input[3:], Main.playlistService.getAllIds(), Main.playlistService.getAll()) if(len(_input) > 3) else []

                _entity = Playlist(name = _name, playWatchedStreams = _playWatchedStreams, allowDuplicates = _allowDuplicates, streamSourceIds = _streamSourceIds)
                _result = Main.playlistService.add(_entity)
                if(_result != None):
                    printS("Playlist \"", _result.name, "\" added successfully.", color = colors["OKGREEN"])
                else:
                    printS("Failed to create Playlist.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in Main.utility.addPlaylistFromYouTubeCommands):
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
                    printS("Failed to create Playlist.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in Main.utility.deletePlaylistCommands):
                # Expected input: playlistIds or indices
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                
                if(len(_ids) == 0):
                    printS("Failed to delete Playlists, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                for _id in _ids:
                    _result = Main.playlistService.delete(_id)
                    if(_result != None):
                        printS("Playlist \"", _result.name, "\" deleted successfully.", color = colors["OKGREEN"])
                    else:
                        printS("Failed to delete Playlist.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in Main.utility.restorePlaylistCommands):
                # Expected input: playlistIds or indices
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                
                if(len(_ids) == 0):
                    printS("Failed to restore Playlists, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                for _id in _ids:
                    _result = Main.playlistService.restore(_id)
                    if(_result != None):
                        printS("Playlist \"", _result.name, "\" restore successfully.", color = colors["OKGREEN"])
                    else:
                        printS("Failed to restore Playlist.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in Main.utility.listPlaylistCommands):
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
            
            elif(arg in Main.utility.detailsPlaylistCommands):
                # Expected input: playlistIds or indices, includeUri, includeId, includeDatertime, includeListCount, includeSource
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True)
                _lenIds = len(_ids)
                _includeUri = eval(_input[_lenIds]) if(len(_input) > _lenIds) else False
                _includeId = eval(_input[_lenIds + 1]) if(len(_input) > _lenIds + 1) else False
                _includeDatetime = eval(_input[_lenIds + 2]) if(len(_input) > _lenIds + 2) else False
                _includeListCount = eval(_input[_lenIds + 3]) if(len(_input) > _lenIds + 3) else True
                _includeSource = eval(_input[_lenIds + 4]) if(len(_input) > _lenIds + 4) else True
                
                if(len(_ids) == 0):
                    printS("Failed to print details, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _result = Main.playlistService.printPlaylistDetails(_ids, _includeUri, _includeId, _includeDatetime, _includeListCount, _includeSource)
                if(_result):
                    printS("Finished printing ", _result, " details.", color = colors["OKGREEN"])
                else:
                    printS("Failed print details.", color = colors["FAIL"])
                        
                argIndex += len(_input) + 1
                continue

            elif(arg in Main.utility.fetchPlaylistSourcesCommands):
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

            elif(arg in Main.utility.prunePlaylistCommands):
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
                    _result = Main.sharedService.prune(_id, _includeSoftDeleted, _permanentlyDelete)
                    _playlist = Main.playlistService.get(_id)
                    
                    if(len(_result["QueueStream"]) > 0 and len(_result["QueueStreamId"]) > 0):
                        printS("Prune finished, deleted ", len(_result["QueueStream"]), " streams, ", len(_result["QueueStreamId"]), " IDs from Playlist \"", _playlist.name, "\".", color = colors["OKGREEN"])
                    else:
                        printS("Prune failed, could not delete any streams from Playlist \"", _playlist.name, "\".", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in Main.utility.purgePlaylistCommands):
                # Expected input: includeSoftDeleted, permanentlyDelete, "accept changes" input within purge method
                _input = extractArgs(argIndex, argV)
                _includeSoftDeleted = eval(_input[0]) if(len(_input) > 0) else False
                _permanentlyDelete = eval(_input[1]) if(len(_input) > 1) else False
                
                _result = Main.sharedService.purge(_includeSoftDeleted, _permanentlyDelete)
                if(len(_result["QueueStream"]) > 0 or len(_result["StreamSource"]) > 0 or len(_result["QueueStreamId"]) > 0 or len(_result["StreamSourceId"]) > 0):
                    printS("Purge finished, deleted ", len(_result["QueueStream"]), " QueueStreams, ", len(_result["StreamSource"]), " StreamSources, and ", len(_result["QueueStreamId"]) + len(_result["StreamSourceId"]), " IDs.", color = colors["OKGREEN"])
                else:
                    printS("Purge failed.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in Main.utility.resetPlaylistFetchCommands):
                # Expected input: playlistIds or indices
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll())
                
                if(len(_ids) == 0):
                    printS("Failed to reset fetch-status of playlists, missing playlistIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                    
                _result = Main.fetchService.resetPlaylistFetch(_ids)
                _playlist = Main.playlistService.get(_id)
                if(_result):
                    printS("Finished resetting fetch statuses for sources in Playlist \"", _playlist.name, "\".", color = colors["OKGREEN"])
                else:
                    printS("Failed to reset fetch statuses for sources in Playlist \"", _playlist.name, "\".", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in Main.utility.playCommands):
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
                    printS("Failed to play Playlist \"", _playlist.name, "\".", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            # Streams
            elif(arg in Main.utility.addStreamCommands):
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
                if(_name == None):
                    _name = "New QueueStream"
                    printS("Could not automatically get the web name for this QueueStream, will be named \"" , _name, "\".", color = colors["WARNING"])

                _playlist = Main.playlistService.get(_ids[0])
                _entity = QueueStream(name = _name, uri = _uri)
                _addResult = Main.playlistService.addStreams(_playlist.id, [_entity])
                if(len(_addResult) > 0):
                    printS("QueueStream \"", _addResult[0].name, "\" added successfully.", color = colors["OKGREEN"])
                else:
                    printS("Failed to create QueueStream.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in Main.utility.deleteStreamCommands):
                # Expected input: playlistId or index, queueStreamIds or indices
                _input = extractArgs(argIndex, argV)

                _playlistIds = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
                if(len(_playlistIds) == 0):
                    printS("Failed to delete QueueStreams, missing playlistId or index.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _playlist = Main.playlistService.get(_playlistIds[0])
                _queueStreamIds = Main.utility.getIdsFromInput(_input[1:], _playlist.streamIds, Main.playlistService.getStreamsByPlaylistId(_playlist.id))
                if(len(_queueStreamIds) == 0):
                    printS("Failed to delete QueueStreams, missing queueStreamIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _result = Main.playlistService.deleteStreams(_playlist.id, _queueStreamIds)
                if(len(_result) > 0):
                    printS("Deleted ", len(_result), " QueueStreams successfully from Playlist \"", _playlist.name, "\".", color = colors["OKGREEN"])
                else:
                    printS("Failed to delete QueueStreams.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in Main.utility.restoreStreamCommands):
                # Expected input: playlistId or index, queueStreamIds or indices
                _input = extractArgs(argIndex, argV)

                _playlistIds = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
                if(len(_playlistIds) == 0):
                    printS("Failed to restore QueueStreams, missing playlistId or index.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _playlist = Main.playlistService.get(_playlistIds[0])
                _queueStreamIds = Main.utility.getIdsFromInput(_input[1:], Main.queueStreamService.getAllIds(includeSoftDeleted = True), Main.playlistService.getStreamsByPlaylistId(_playlist.id, includeSoftDeleted = True))
                if(len(_queueStreamIds) == 0):
                    printS("Failed to restore QueueStreams, missing queueStreamIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _result = Main.playlistService.restoreStreams(_playlist.id, _queueStreamIds)
                if(len(_result) > 0):
                    printS("Restored ", len(_result), " QueueStreams successfully from Playlist \"", _playlist.name, "\".", color = colors["OKGREEN"])
                else:
                    printS("Failed to restore QueueStreams.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            # Sources
            elif(arg in Main.utility.addSourcesCommands):
                # Expected input: playlistId or index, uri, enableFetch?, backgroundContent?, name?
                _input = extractArgs(argIndex, argV)
                _ids = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
                _uri = _input[1] if len(_input) > 1 else None
                _enableFetch = eval(_input[2]) if len(_input) > 2 else False
                _bgContent = eval(_input[3]) if len(_input) > 3 else False
                _name = _input[4] if len(_input) > 4 else None

                if(len(_ids) == 0):
                    printS("Failed to add StreamSource, missing playlistId or index.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue

                if(_uri == None):
                    printS("Failed to add StreamSource, missing uri.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue

                if(_name == None):
                    _name = Main.utility.getPageTitle(_uri)
                if(_name == None):
                    _name = "New StreamSource"
                    printS("Could not automatically get the web name for this StreamSource, will be named \"" , _name, "\".", color = colors["WARNING"])                  
                    
                _playlist = Main.playlistService.get(_ids[0])
                _entity = StreamSource(name = _name, uri = _uri, enableFetch = _enableFetch, backgroundContent = _bgContent)
                _addResult = Main.playlistService.addStreamSources(_playlist.id, [_entity])
                if(len(_addResult) > 0):
                    printS("StreamSource \"", _addResult[0].name, "\" added successfully.", color = colors["OKGREEN"])
                else:
                    printS("Failed to create StreamSource.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in Main.utility.deleteSourceCommands):
                # Expected input: playlistId or index, streamSourceIds or indices
                _input = extractArgs(argIndex, argV)

                _playlistIds = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
                if(len(_playlistIds) == 0):
                    printS("Failed to delete StreamSources, missing playlistId or index.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _playlist = Main.playlistService.get(_playlistIds[0])
                _streamSourceIds = Main.utility.getIdsFromInput(_input[1:], _playlist.streamSourceIds, Main.playlistService.getSourcesByPlaylistId(_playlist.id))
                if(len(_streamSourceIds) == 0):
                    printS("Failed to delete StreamSources, missing streamSourceIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _result = Main.playlistService.deleteStreamSources(_playlist.id, _streamSourceIds)
                if(len(_result) > 0):
                    printS("Deleted ", len(_result), " StreamSources successfully from playlist \"", _playlist.name, "\".", color = colors["OKGREEN"])
                else:
                    printS("Failed to delete StreamSources.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue
            
            elif(arg in Main.utility.restoreSourceCommands):
                # Expected input: playlistId or index, streamSourceIds or indices
                _input = extractArgs(argIndex, argV)

                _playlistIds = Main.utility.getIdsFromInput(_input, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1)
                if(len(_playlistIds) == 0):
                    printS("Failed to restore StreamSources, missing playlistId or index.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _playlist = Main.playlistService.get(_playlistIds[0])
                _streamSourceIds = Main.utility.getIdsFromInput(_input[1:], Main.streamSourceService.getAllIds(includeSoftDeleted = True), Main.playlistService.getSourcesByPlaylistId(_playlist.id, includeSoftDeleted = True))
                if(len(_streamSourceIds) == 0):
                    printS("Failed to restore StreamSources, missing streamSourceIds or indices.", color = colors["FAIL"])
                    argIndex += len(_input) + 1
                    continue
                
                _result = Main.playlistService.restoreStreamSources(_playlist.id, _streamSourceIds)
                if(len(_result) > 0):
                    printS("Restored ", len(_result), " StreamSources successfully from Playlist \"", _playlist.name, "\".", color = colors["OKGREEN"])
                else:
                    printS("Failed to restore StreamSources.", color = colors["FAIL"])

                argIndex += len(_input) + 1
                continue

            elif(arg in Main.utility.listSourcesCommands):
                # Expected input: includeSoftDeleted
                _input = extractArgs(argIndex, argV)
                _includeSoftDeleted = eval(_input[0]) if(len(_input) > 0) else False

                _result = Main.streamSourceService.getAll(_includeSoftDeleted)
                if(len(_result) > 0):
                    for (i, _entry) in enumerate(_result):
                        printS(i, " - ", _entry.summaryString())
                else:
                    printS("No QueueStreams found.", color = colors["WARNING"])

                argIndex += len(_input) + 1
                continue

            # Meta
            elif(arg in Main.utility.listSettingsCommands):
                # Expected input: none
                
                _result = Main.utility.getAllSettingsAsString()
                print(_result)

                argIndex += 1
                continue
            
            elif(arg in Main.utility.listSoftDeletedCommands):
                # Expected input: simplified
                _input = extractArgs(argIndex, argV)
                _simplified = eval(_input[0]) if(len(_input) > 0) else False
                
                _result = Main.sharedService.getAllSoftDeleted()
                if(_simplified):
                    _resultList = [[e.summaryString() for e in l] for l in [*_result.values()]]
                else: 
                    _resultList = [[e.detailsString() for e in l] for l in [*_result.values()]]
                    
                Main.utility.printLists(_resultList, [*_result.keys()])

                argIndex += len(_input) + 1
                continue

            # Invalid
            else:
                printS("Argument not recognized: \"", arg, "\", please see documentation or run with \"-help\" for help.", color = colors["WARNING"])
                argIndex += 1

if __name__ == "__main__":
    Main.main()
