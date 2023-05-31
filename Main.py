import os
import sys

from grdUtil.BashColor import BashColor
from grdUtil.FileUtil import makeFiles
from grdUtil.InputUtil import extractArgs, getIdsFromInput, getIfExists
from grdUtil.PrintUtil import printLists, printS
from pytube import Channel

from Commands import Commands
from controllers.PlaylistCliController import PlaylistCliController
from controllers.QueueStreamCliController import QueueStreamCliController
from controllers.SharedCliController import SharedCliController
from controllers.StreamSourceCliController import StreamSourceCliController
from services.DownloadService import DownloadService
from services.FetchService import FetchService
from services.LegacyService import LegacyService
from services.PlaylistService import PlaylistService
from services.SharedService import SharedService
from services.StreamSourceService import StreamSourceService
from Settings import Settings


class Main:
    commands: Commands = Commands()
    settings: Settings = Settings()
    downloadService: DownloadService = DownloadService()
    fetchService: FetchService = FetchService()
    legacyService: LegacyService = LegacyService()
    playlistService: PlaylistService = PlaylistService()
    sharedService: SharedService = SharedService()
    streamSourceService: StreamSourceService = StreamSourceService()
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
                    
                    
                    x = [1, 2, 3, 4, 5, 6, 7]
                    printS(x[None:None])
                    c = int(None)
                    
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
                    
                    resultList = []
                    resultList.append([" - ".join([e.id, e.name]) for e in result.playlists])
                    resultList.append([" - ".join([e.id, e.name]) for e in result.streamSources])
                    resultList.append([" - ".join([e.id, e.name]) for e in result.queueStreams])
                    printLists(resultList, ["playlists", "streamSources", "queueStreams"])
                    
                    argIndex += len(inputArgs) + 1
                    continue
                
                # Playlist
                elif(arg in Main.commands.addPlaylistCommands):
                    # Expected input: name, playWatchedStreams?, allowDuplicates?, streamSourceIds/indices?
                    inputArgs = extractArgs(argIndex, argV)
                    name = inputArgs[0] if(len(inputArgs) > 0) else "New Playlist"
                    playWatchedStreams = eval(inputArgs[1]) if(len(inputArgs) > 1) else True
                    allowDuplicates = eval(inputArgs[2]) if(len(inputArgs) > 2) else False
                    streamSourceIds = getIdsFromInput(inputArgs[3:], Main.playlistService.getAllIds(), Main.playlistService.getAll(), debug = Main.settings.debug) if(len(inputArgs) > 3) else []

                    Main.playlistCliController.addPlaylist(name, playWatchedStreams, allowDuplicates, streamSourceIds)
                    
                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.addPlaylistFromYouTubeCommands):
                    # Expected input: youTubePlaylistUrl, name?, playWatchedStreams?, allowDuplicates?
                    inputArgs = extractArgs(argIndex, argV)
                    url = inputArgs[0] if(len(inputArgs) > 0) else None
                    name = inputArgs[1] if(len(inputArgs) > 1) else None
                    playWatchedStreams = eval(inputArgs[2]) if(len(inputArgs) > 2) else True
                    allowDuplicates = eval(inputArgs[3]) if(len(inputArgs) > 3) else False

                    Main.playlistCliController.addYouTubePlaylist(url, name, playWatchedStreams, allowDuplicates)
                    
                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.deletePlaylistCommands):
                    # Expected input: playlistIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), debug = Main.settings.debug)
                    
                    Main.playlistCliController.deletePlaylists(playlistIds)

                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.restorePlaylistCommands):
                    # Expected input: playlistIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(True), Main.playlistService.getAll(True), debug = Main.settings.debug)
                    
                    Main.playlistCliController.restorePlaylists(playlistIds)
                    
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
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True, debug = Main.settings.debug)
                    lenPlaylistIds = len(playlistIds)
                    includeUri = eval(inputArgs[lenPlaylistIds]) if(len(inputArgs) > lenPlaylistIds) else False
                    includeId = eval(inputArgs[lenPlaylistIds + 1]) if(len(inputArgs) > lenPlaylistIds + 1) else False
                    includeDatetime = eval(inputArgs[lenPlaylistIds + 2]) if(len(inputArgs) > lenPlaylistIds + 2) else False
                    includeListCount = eval(inputArgs[lenPlaylistIds + 3]) if(len(inputArgs) > lenPlaylistIds + 3) else True
                    includeSource = eval(inputArgs[lenPlaylistIds + 4]) if(len(inputArgs) > lenPlaylistIds + 4) else True
                    
                    Main.playlistCliController.printPlaylistsDetailed(playlistIds, includeUri, includeId, includeDatetime, includeListCount, includeSource)
                            
                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.ListWatchedCommands):
                    # Expected input: playlistIds or indices, includeUri, includeId, includeDatetime, includeListCount, includeSource
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True, debug = Main.settings.debug)
                    lenPlaylistIds = len(playlistIds)
                    
                    Main.playlistCliController.printWatchedStreams(playlistIds)
                            
                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.fetchPlaylistSourcesCommands):
                    # Expected input: playlistIds or indices, fromDateTime?, toDatetime?, takeNewOnly?
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True, debug = Main.settings.debug)
                    lenPlaylistIds = len(playlistIds)
                    takeAfter = inputArgs[lenPlaylistIds] if(len(inputArgs) > lenPlaylistIds) else None
                    takeBefore = inputArgs[lenPlaylistIds + 1] if(len(inputArgs) > lenPlaylistIds + 1) else None
                    takeNewOnly = eval(inputArgs[lenPlaylistIds + 2]) if(len(inputArgs) > lenPlaylistIds + 2) else True
                    
                    Main.playlistCliController.fetchPlaylists(playlistIds, Main.settings.fetchLimitSingleSource, takeAfter, takeBefore, takeNewOnly)

                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.prunePlaylistCommands):
                    # Expected input: playlistIds or indices, includeSoftDeleted, permanentlyDelete, "accept changes" input within method
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), returnOnNonIds = True, debug = Main.settings.debug)
                    lenPlaylistIds = len(playlistIds)
                    includeSoftDeleted = eval(getIfExists(inputArgs, lenPlaylistIds, "False"))
                    permanentlyDelete = eval(getIfExists(inputArgs, lenPlaylistIds + 1, "False"))
                    
                    for id in playlistIds:
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
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), debug = Main.settings.debug)
                    
                    Main.playlistCliController.resetPlaylists(playlistIds)

                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.playCommands):
                    # Expected input: playlistId or index, startIndex, shuffle, repeat
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, debug = Main.settings.debug)
                    startIndex = inputArgs[1] if(len(inputArgs) > 1) else 0
                    shuffle = eval(inputArgs[2]) if(len(inputArgs) > 2) else False
                    repeat = eval(inputArgs[3]) if(len(inputArgs) > 3) else False
                    
                    Main.playlistCliController.playPlaylists(getIfExists(playlistIds, 0), int(startIndex), shuffle, repeat)

                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.downloadPlaylistCommands):
                    # Expected input: playlistId or index, directoryName?, startIndex?, endIndex?, streamNameRegex?, useIndex?
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, debug = Main.settings.debug)
                    directoryName = inputArgs[1] if(len(inputArgs) > 1) else None
                    startIndex = int(inputArgs[2]) if(len(inputArgs) > 2) else None
                    endIndex = int(inputArgs[3]) if(len(inputArgs) > 3) else None
                    streamNameRegex = inputArgs[4] if(len(inputArgs) > 4) else None
                    useIndex = eval(inputArgs[5]) if(len(inputArgs) > 5) else True
                    
                    Main.playlistCliController.downloadPlaylist(getIfExists(playlistIds, 0), directoryName, startIndex, endIndex, streamNameRegex, useIndex)
                    
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
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(True), Main.playlistService.getAll(True), 1, setDefaultId = False, debug = Main.settings.debug)
                    queueStreamIds = inputArgs[1:] if len(inputArgs) > 1 else []
                                        
                    Main.queueStreamCliController.restoreQueueStreams(getIfExists(playlistIds, 0), queueStreamIds)

                    argIndex += len(inputArgs) + 1
                    continue

                # Sources
                elif(arg in Main.commands.addSourcesCommands):
                    # Expected input: playlistId or index, uri, enableFetch?, backgroundContent?, name?
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, debug = Main.settings.debug)
                    uri = inputArgs[1] if len(inputArgs) > 1 else None
                    enableFetch = eval(inputArgs[2]) if len(inputArgs) > 2 else True
                    bgContent = eval(inputArgs[3]) if len(inputArgs) > 3 else False
                    name = inputArgs[4] if len(inputArgs) > 4 else None
                    
                    Main.streamSourceCliController.addStreamSource(getIfExists(playlistIds, 0), uri, enableFetch, bgContent, name)

                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.deleteSourceCommands):
                    # Expected input: playlistId or index, streamSourceIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(), Main.playlistService.getAll(), 1, debug = Main.settings.debug)
                    streamSourceIds = inputArgs[1:] if len(inputArgs) > 1 else []

                    Main.streamSourceCliController.deleteStreamSources(getIfExists(playlistIds, 0), streamSourceIds)
                    
                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.restoreSourceCommands):
                    # Expected input: playlistId or index, streamSourceIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIds(True), Main.playlistService.getAll(True), 1, debug = Main.settings.debug)
                    streamSourceIds = inputArgs[1:] if len(inputArgs) > 1 else []
                    
                    Main.streamSourceCliController.restoreStreamSources(getIfExists(playlistIds, 0), streamSourceIds)

                    argIndex += len(inputArgs) + 1
                    continue

                elif(arg in Main.commands.listSourcesCommands):
                    # Expected input: includeSoftDeleted
                    inputArgs = extractArgs(argIndex, argV)
                    includeSoftDeleted = eval(inputArgs[0]) if(len(inputArgs) > 0) else False
                    
                    Main.streamSourceCliController.listStreamSources(includeSoftDeleted)

                    argIndex += len(inputArgs) + 1
                    continue
                
                elif(arg in Main.commands.openSourceCommands):
                    # Expected input: streamSourceIds or indices
                    inputArgs = extractArgs(argIndex, argV)
                    streamSourceIds = getIdsFromInput(inputArgs, Main.streamSourceService.getAllIds(), Main.streamSourceService.getAll(), debug = Main.settings.debug)
                    
                    Main.streamSourceCliController.openStreamSource(streamSourceIds)

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
            printS("Program was aborted by user.", color = BashColor.OKGREEN)

if __name__ == "__main__":
    Main.main()
