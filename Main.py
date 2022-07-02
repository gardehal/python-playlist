import os
import subprocess
import sys
from datetime import datetime

from grdUtil.BashColor import BashColor
from grdUtil.FileUtil import makeFiles
from grdUtil.InputUtil import (extractArgs, getIdsFromInput, getIfExists,
                               isNumber)
from grdUtil.PrintUtil import printLists, printS

from Commands import Commands
from controllers.CliController import SharedCliController
from controllers.PlaylistCliController import PlaylistCliController
from controllers.QueueStreamCliController import QueueStreamCliController
from controllers.StreamSourceCliController import StreamSourceCliController
from model.StreamSource import StreamSource
from services.LegacyService import LegacyService
from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.SharedService import SharedService
from services.StreamSourceService import StreamSourceService
from Settings import Settings


class Main:
    legacyService = LegacyService()
    playlistService = PlaylistService()
    queueStreamService = QueueStreamService()
    sharedService = SharedService()
    streamSourceService = StreamSourceService()
    commands = Commands()
    settings = Settings()
    sharedCliController: SharedCliController = SharedCliController()
    playlistCliController: PlaylistCliController = PlaylistCliController()
    queueStreamCliController: QueueStreamCliController = QueueStreamCliController()
    streamSourceCliController: StreamSourceCliController = StreamSourceCliController()

    def main():
        argC = len(sys.argv)
        argV = sys.argv
        argIndex = 1

        if(argC < 2):
            help = Main.commands.getHelpString()
            printS(help)

        makeFiles(Main.settings.watchedLogFilepath)

        try:
            while argIndex < argC:
                arg = sys.argv[argIndex].lower()

                if(arg in Main.commands.helpCommands):
                    help = Main.commands.getHelpString()
                    printS(help)
                    
                    argIndex += 1
                    continue

                elif(arg in Main.commands.testCommands):
                    inputArgs = extractArgs(argIndex, argV)
                    printS("Test", color = BashColor.OKBLUE)
                    
                    print(type(None))
                    
                    quit()            
                    
                elif(arg in Main.commands.editCommands):
                    # Expected input: playlistId or index
                    inputArgs = extractArgs(argIndex, argV)
                    
                    ids = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), debug = Main.settings.debug)
                    if(len(ids) == 0):
                        printS("Failed to edit, missing playlistId or index.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue

                    filepath = os.path.join(Main.settings.localStoragePath, "Playlist", ids[0] + ".json")
                    filepath = str(filepath).replace("\\", "/")
                    os.startfile(filepath)
                        
                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.searchCommands):
                    # Expected input: searchTerm, includeSoftDeleted?
                    inputArgs = extractArgs(argIndex, argV)
                    searchTerm = inputArgs[0] if(len(inputArgs) > 0) else ""
                    includeSoftDeleted = eval(inputArgs[1]) if(len(inputArgs) > 1) else False

                    result = Main.sharedService.search(searchTerm, includeSoftDeleted)
                    
                    # result is a dict of string keys, list values, get values from [*result.values()]
                    # list of list, for each list, for each entry, str.join id, name, and uri, then join back to list of lists of strings, ready for printLists
                    resultList = [[" - ".join([e.id, e.name]) for e in l] for l in [*result.values()]]
                    printLists(resultList, [*result.keys()])
                    
                    argIndex += len(inputArgs) + 1
                    continue
                
                # Playlist
                elif(arg in Main.commands.addPlaylistCommands):
                    # Expected input: name, playWatchedStreams?, allowDuplicates?, streamSourceIds/indices?
                    inputArgs = extractArgs(argIndex, argV)
                    name = inputArgs[0] if(len(inputArgs) > 0) else "New Playlist"
                    playWatchedStreams = eval(inputArgs[1]) if(len(inputArgs) > 1) else None
                    allowDuplicates = eval(inputArgs[2]) if(len(inputArgs) > 2) else True
                    streamSourceIds = getIdsFromInput(inputArgs[3:], Main.playlistService.getAllIds(), Main.playlistService.getAll(), debug = Main.settings.debug) if(len(inputArgs) > 3) else []

                    Main.playlistCliController.addPlaylist(name, playWatchedStreams, allowDuplicates, streamSourceIds)
                    
                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.addPlaylistFromYouTubeCommands):
                    # Expected input: youTubePlaylistUrl, name?, playWatchedStreams?, allowDuplicates?
                    inputArgs = extractArgs(argIndex, argV)
                    url = inputArgs[0] if(len(inputArgs) > 0) else None
                    name = inputArgs[1] if(len(inputArgs) > 1) else None
                    playWatchedStreams = eval(inputArgs[2]) if(len(inputArgs) > 2) else None
                    allowDuplicates = eval(inputArgs[3]) if(len(inputArgs) > 3) else True

                    Main.playlistCliController.addPlaylist(url, name, playWatchedStreams, allowDuplicates)
                    
                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.deletePlaylistCommands):
                    # Expected input: playlistIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    ids = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), debug = Main.settings.debug)
                    
                    if(len(ids) == 0):
                        printS("Failed to delete Playlists, missing playlistIds or indices.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue
                    
                    Main.playlistCliController.deletePlaylists(ids)

                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.restorePlaylistCommands):
                    # Expected input: playlistIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    ids = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), debug = Main.settings.debug)
                    
                    if(len(ids) == 0):
                        printS("Failed to restore Playlists, missing playlistIds or indices.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue

                    Main.playlistCliController.restorePlaylists(ids)
                    
                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.listPlaylistCommands):
                    # Expected input: includeSoftDeleted?
                    inputArgs = extractArgs(argIndex, argV)
                    includeSoftDeleted = eval(inputArgs[0]) if(len(inputArgs) > 0) else False
                        
                    Main.playlistCliController.printPlaylists(includeSoftDeleted)

                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.detailsPlaylistCommands):
                    # Expected input: playlistIds or indices, includeUri, includeId, includeDatetime, includeListCount, includeSource
                    inputArgs = extractArgs(argIndex, argV)
                    ids = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True, debug = Main.settings.debug)
                    lenIds = len(ids)
                    includeUri = eval(inputArgs[lenIds]) if(len(inputArgs) > lenIds) else False
                    includeId = eval(inputArgs[lenIds + 1]) if(len(inputArgs) > lenIds + 1) else False
                    includeDatetime = eval(inputArgs[lenIds + 2]) if(len(inputArgs) > lenIds + 2) else False
                    includeListCount = eval(inputArgs[lenIds + 3]) if(len(inputArgs) > lenIds + 3) else True
                    includeSource = eval(inputArgs[lenIds + 4]) if(len(inputArgs) > lenIds + 4) else True
                    
                    if(len(ids) == 0):
                        printS("Failed to print details, missing playlistIds or indices.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue
                    
                    Main.playlistCliController.printPlaylistsDetailed(ids, includeUri, includeId, includeDatetime, includeListCount, includeSource)
                            
                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.fetchPlaylistSourcesCommands):
                    # Expected input: playlistIds or indices, fromDateTime?, toDatetime?, takeNewOnly?
                    inputArgs = extractArgs(argIndex, argV)
                    ids = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True, debug = Main.settings.debug)
                    lenIds = len(ids)
                    takeAfter = inputArgs[lenIds] if(len(inputArgs) > lenIds) else None
                    takeBefore = inputArgs[lenIds + 1] if(len(inputArgs) > lenIds + 1) else None
                    takeNewOnly = eval(inputArgs[lenIds + 2]) if(len(inputArgs) > lenIds + 2) else True
                    
                    try:
                        if(takeAfter != None):
                            takeAfter = datetime.strptime(takeAfter, "%Y-%m-%d")
                        if(takeBefore != None):
                            takeBefore = datetime.strptime(takeBefore, "%Y-%m-%d")
                    except:
                        printS("Dates for takeAfter and takeBefore were not valid, see help print for format.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue
                    
                    Main.playlistCliController.fetchPlaylists(ids, Main.settings.fetchLimitSingleSource, takeAfter, takeBefore, takeNewOnly)

                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.prunePlaylistCommands):
                    # Expected input: playlistIds or indices, includeSoftDeleted, permanentlyDelete, "accept changes" input within method
                    inputArgs = extractArgs(argIndex, argV)
                    ids = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True, debug = Main.settings.debug)
                    lenIds = len(ids)
                    includeSoftDeleted = eval(getIfExists(inputArgs, lenIds, "False"))
                    permanentlyDelete = eval(getIfExists(inputArgs, lenIds + 1, "False"))
                    
                    for id in ids:
                        Main.sharedCliController.prune(id, includeSoftDeleted, permanentlyDelete)

                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.purgePlaylistCommands):
                    # Expected input: "accept changes" input within method
                    
                    Main.sharedCliController.purgePlaylists(True, True)

                    argIndex += 1
                    continue
                
                elif(arg in Main.commands.purgeCommands):
                    # Expected input: "accept changes" input within method

                    Main.sharedCliController.purge()

                    argIndex += 1
                    continue
                
                elif(arg in Main.commands.resetPlaylistFetchCommands):
                    # Expected input: playlistIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    ids = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), debug = Main.settings.debug)
                    
                    if(len(ids) == 0):
                        printS("Failed to reset fetch-status of playlists, missing playlistIds or indices.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue
                    
                    Main.playlistCliController.resetPlaylists(ids)

                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.playCommands):
                    # Expected input: playlistId or index, startIndex, shuffle, repeat
                    inputArgs = extractArgs(argIndex, argV)
                    ids = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, debug = Main.settings.debug)
                    startIndex = inputArgs[1] if(len(inputArgs) > 1) else 0
                    shuffle = eval(inputArgs[2]) if(len(inputArgs) > 2) else False
                    repeat = eval(inputArgs[3]) if(len(inputArgs) > 3) else False
                    
                    if(len(ids) == 0):
                        printS("Failed to play playlist, missing playlistIds or indices.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue
                    
                    if(not isNumber(startIndex, intOnly = True)):
                        printS("Failed to play playlist, input startIndex must be an integer.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue
                    
                    Main.playlistCliController.playPlaylists(ids[0], int(startIndex), shuffle, repeat)

                    argIndex += len(inputArgs) + 1
                    continue

                # Streams
                elif(arg in Main.commands.addStreamCommands):
                    # Expected input: playlistId or index, uri, name?
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, setDefaultId = False, debug = Main.settings.debug)
                    uri = inputArgs[1] if len(inputArgs) > 1 else None
                    name = inputArgs[2] if len(inputArgs) > 2 else None
                    
                    Main.queueStreamCliController.addQueueStream(getIfExists(playlistIds, 0), uri, name)

                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.deleteStreamCommands):
                    # Expected input: playlistId or index, queueStreamIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, setDefaultId = False, debug = Main.settings.debug)
                    queueStreamIds = inputArgs[1:] if len(inputArgs) > 1 else []
                    
                    Main.queueStreamCliController.deleteQueueStreams(getIfExists(playlistIds, 0), queueStreamIds)

                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.restoreStreamCommands):
                    # Expected input: playlistId or index, queueStreamIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, setDefaultId = False, debug = Main.settings.debug)
                    queueStreamIds = inputArgs[1:] if len(inputArgs) > 1 else []
                                        
                    Main.queueStreamCliController.restoreQueueStreams(getIfExists(playlistIds, 0), queueStreamIds)

                    argIndex += len(inputArgs) + 1
                    continue

                # Sources
                elif(arg in Main.commands.addSourcesCommands):
                    # Expected input: playlistId or index, uri, enableFetch?, backgroundContent?, name?
                    inputArgs = extractArgs(argIndex, argV)
                    ids = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, debug = Main.settings.debug)
                    uri = inputArgs[1] if len(inputArgs) > 1 else None
                    enableFetch = eval(inputArgs[2]) if len(inputArgs) > 2 else False
                    bgContent = eval(inputArgs[3]) if len(inputArgs) > 3 else False
                    name = inputArgs[4] if len(inputArgs) > 4 else None

                    if(len(ids) == 0):
                        printS("Failed to add StreamSource, missing playlistId or index.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue

                    if(uri == None):
                        printS("Failed to add StreamSource, missing uri.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue

                    if(name == None):
                        name = Main.sharedService.getPageTitle(uri)
                    if(name == None):
                        name = "New StreamSource"
                        printS("Could not automatically get the web name for this StreamSource, will be named \"" , name, "\".", color = BashColor.WARNING)                  
                        
                    playlist = Main.playlistService.get(ids[0])
                    entity = StreamSource(name = name, uri = uri, enableFetch = enableFetch, backgroundContent = bgContent)
                    addResult = Main.playlistService.addStreamSources(playlist.id, [entity])
                    if(len(addResult) > 0):
                        printS("Added StreamSource \"", addResult[0].name, "\" to Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
                    else:
                        printS("Failed to create StreamSource.", color = BashColor.FAIL)

                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.deleteSourceCommands):
                    # Expected input: playlistId or index, streamSourceIds or indices
                    inputArgs = extractArgs(argIndex, argV)

                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, debug = Main.settings.debug)
                    if(len(playlistIds) == 0):
                        printS("Failed to delete StreamSources, missing playlistId or index.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue
                    
                    playlist = Main.playlistService.get(playlistIds[0])
                    streamSourceIds = getIdsFromInput(inputArgs[1:], playlist.streamSourceIds, Main.playlistService.getSourcesByPlaylistId(playlist.id), debug = Main.settings.debug)
                    if(len(streamSourceIds) == 0):
                        printS("Failed to delete StreamSources, missing streamSourceIds or indices.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue
                    
                    result = Main.playlistService.deleteStreamSources(playlist.id, streamSourceIds)
                    if(len(result) > 0):
                        printS("Deleted ", len(result), " StreamSources successfully from playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
                    else:
                        printS("Failed to delete StreamSources.", color = BashColor.FAIL)

                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.restoreSourceCommands):
                    # Expected input: playlistId or index, streamSourceIds or indices
                    inputArgs = extractArgs(argIndex, argV)

                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, debug = Main.settings.debug)
                    if(len(playlistIds) == 0):
                        printS("Failed to restore StreamSources, missing playlistId or index.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue
                    
                    playlist = Main.playlistService.get(playlistIds[0])
                    streamSourceIds = getIdsFromInput(inputArgs[1:], Main.streamSourceService.getAllIds(includeSoftDeleted = True), Main.playlistService.getSourcesByPlaylistId(playlist.id, includeSoftDeleted = True), debug = Main.settings.debug)
                    if(len(streamSourceIds) == 0):
                        printS("Failed to restore StreamSources, missing streamSourceIds or indices.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue
                    
                    result = Main.playlistService.restoreStreamSources(playlist.id, streamSourceIds)
                    if(len(result) > 0):
                        printS("Restored ", len(result), " StreamSources successfully from Playlist \"", playlist.name, "\".", color = BashColor.OKGREEN)
                    else:
                        printS("Failed to restore StreamSources.", color = BashColor.FAIL)

                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.listSourcesCommands):
                    # Expected input: includeSoftDeleted
                    inputArgs = extractArgs(argIndex, argV)
                    includeSoftDeleted = eval(inputArgs[0]) if(len(inputArgs) > 0) else False

                    result = Main.streamSourceService.getAll(includeSoftDeleted)
                    if(len(result) > 0):
                        for (i, entry) in enumerate(result):
                            printS(i, " - ", entry.summaryString())
                    else:
                        printS("No QueueStreams found.", color = BashColor.WARNING)

                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.openSourceCommands):
                    # Expected input: streamSourceIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    
                    streamSourceIds = getIdsFromInput(inputArgs, Main.streamSourceService.getAllIds(), Main.streamSourceService.getAll(), debug = Main.settings.debug)
                    if(len(streamSourceIds) == 0):
                        printS("Failed to open StreamSources, missing streamSourceIds or indices.", color = BashColor.FAIL)
                        argIndex += len(inputArgs) + 1
                        continue

                    for id in streamSourceIds:
                        stream = Main.streamSourceService.get(id)
                        if(stream != None):
                            subprocess.Popen(f"call start {stream.uri}", stdout = subprocess.PIPE, shell = True)
                    
                        else:
                            printS("No StreamSource found.", color = BashColor.WARNING)

                    argIndex += len(inputArgs) + 1
                    continue

                # Meta
                elif(arg in Main.commands.listSettingsCommands):
                    # Expected input: none
                    
                    result = Main.settings.getAllSettingsAsTable()
                    print(result)

                    argIndex += 1
                    continue
                
                elif(arg in Main.commands.listSoftDeletedCommands):
                    # Expected input: simplified
                    inputArgs = extractArgs(argIndex, argV)
                    simplified = eval(inputArgs[0]) if(len(inputArgs) > 0) else False
                    
                    result = Main.sharedService.getAllSoftDeleted()
                    if(simplified):
                        resultList = [[e.summaryString() for e in l] for l in [*result.values()]]
                    else: 
                        resultList = [[e.detailsString() for e in l] for l in [*result.values()]]
                        
                    printLists(resultList, [*result.keys()])

                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.refactorCommands):
                    # Expected input: None
                    
                    refactorLastFetchedIdResult = Main.legacyService.refactorLastFetchedId()
                    if(len(refactorLastFetchedIdResult) > 0):
                        printS("Refactored ", len(refactorLastFetchedIdResult), " StreamSources. IDs:", color = BashColor.OKGREEN)
                        printS(refactorLastFetchedIdResult)
                    else:
                        printS("No refactors needed for refactorLastFetchedId.", color = BashColor.OKGREEN)

                    argIndex += 1
                    continue

                # Invalid
                else:
                    printS("Argument not recognized: \"", arg, "\", please see documentation or run with \"help\" for help.", color = BashColor.WARNING)
                    argIndex += 1
                    
        except KeyboardInterrupt:
            printS("Program was aborted by user.", color = BashColor.WARNING)

if __name__ == "__main__":
    Main.main()
