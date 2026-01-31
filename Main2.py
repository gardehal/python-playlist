import os
import sys

from grdUtil.BashColor import BashColor
from grdUtil.FileUtil import makeFiles
from grdUtil.PrintUtil import printLists, printS
from Argumentor import *
from enums.CommandHitValues import CommandHitValues

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
        makeFiles(Main.settings.watchedLogFilepath)
        
        argumentor = Main.commands.getArgumentor()
        results = argumentor.validate(sys.argv)
        try:
            for result in results:
                # print(result.toString()) # For debugging
                if(not result.isValid):
                    print(f"Input for {result.commandName} was not valid:")
                    print(result.getFormattedMessages())
                    continue

                if(result.messages):
                    print(f"Command {result.commandName} was accepted with modifications:")
                    print(result.getFormattedMessages())

                if(result.commandHitValue == CommandHitValues.HELP):
                    print(argumentor.getFormattedDescription())

                elif(result.commandHitValue == CommandHitValues.TEST):
                    printS("Test", color = BashColor.OKBLUE)
                    # Test code here
                    quit()
                    
                elif(result.commandHitValue == CommandHitValues.EDIT):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]

                    filepath = os.path.join(Main.settings.localStoragePath, "Playlist", playlistIds[0] + ".json")
                    filepath = str(filepath).replace("\\", "/")
                    os.startfile(filepath)
                    
                elif(result.commandHitValue == CommandHitValues.SEARCH):
                    searchTerm = result.arguments[Main.commands.searchQueryArgumentName]
                    includeSoftDeleted = result.arguments[Main.commands.includeSoftDeletedFlagName]

                    searchResult = Main.sharedService.search(searchTerm, includeSoftDeleted)
                    
                    resultList = []
                    resultList.append([" - ".join([e.id, e.name]) for e in searchResult.playlists])
                    resultList.append([" - ".join([e.id, e.name]) for e in searchResult.streamSources])
                    resultList.append([" - ".join([e.id, e.name]) for e in searchResult.queueStreams])
                    printLists(resultList, ["playlists", "streamSources", "queueStreams"])
                    
                # Playlist
                elif(result.commandHitValue == CommandHitValues.ADD_PLAYLIST):
                    name = result.arguments[Main.commands.entityNameArgumentName]
                    playWatchedStreams = result.arguments[Main.commands.playWatchedStreamsFlagName]
                    allowDuplicates = result.arguments[Main.commands.allowDuplicatesFlagName]
                    streamSourceIds = result.arguments[Main.commands.streamSourceIdsArgumentName]
                    
                    Main.playlistCliController.addPlaylist(name, playWatchedStreams, allowDuplicates, streamSourceIds)
                    
                elif(result.commandHitValue == CommandHitValues.ADD_PLAYLIST_FROM_YOUTUBE):
                    url = result.arguments[Main.commands.uriArgumentName]
                    name = result.arguments[Main.commands.entityNameArgumentName]
                    playWatchedStreams = result.arguments[Main.commands.playWatchedStreamsFlagName]
                    allowDuplicates = result.arguments[Main.commands.allowDuplicatesFlagName]
                    
                    Main.playlistCliController.addYouTubePlaylist(url, name, playWatchedStreams, allowDuplicates)
                    
                elif(result.commandHitValue == CommandHitValues.DELETE_PLAYLIST):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    
                    Main.playlistCliController.deletePlaylists(playlistIds)
                    
                elif(result.commandHitValue == CommandHitValues.RESTORE_PLAYLIST):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    
                    Main.playlistCliController.restorePlaylists(playlistIds)
                    
                elif(result.commandHitValue == CommandHitValues.LIST_PLAYLISTS):
                    includeSoftDeleted = result.arguments[Main.commands.includeSoftDeletedFlagName]
                    
                    Main.playlistCliController.printPlaylists(includeSoftDeleted)
                    
                elif(result.commandHitValue == CommandHitValues.DETAILS_PLAYLIST):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    includeUri = result.arguments[Main.commands.includeUriFlagName]
                    includeId = result.arguments[Main.commands.includeIdFlagName]
                    includeDatetime = result.arguments[Main.commands.includeDateTimeFlagName]
                    includeListCount = result.arguments[Main.commands.includeListCountFlagName]
                    includeSource = result.arguments[Main.commands.includeSourceFlagName]
                    
                    Main.playlistCliController.printPlaylistsDetailed(playlistIds, includeUri, includeId, includeDatetime, includeListCount, includeSource)
                    
                # elif(result.commandHitValue == CommandHitValues.ListWatchedCommands):
                #     playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    
                #     Main.playlistCliController.printWatchedStreams(playlistIds)
                    
                elif(result.commandHitValue == CommandHitValues.FETCH_PLAYLIST):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    takeAfter = result.arguments[Main.commands.takeAfterArgumentName]
                    takeBefore = result.arguments[Main.commands.takeBeforeArgumentName]
                    takeNewOnly = result.arguments[Main.commands.takeNewOnlyFlagName]
                    
                    Main.playlistCliController.fetchPlaylists(playlistIds, Main.settings.fetchLimitSingleSource, takeAfter, takeBefore, takeNewOnly)
                    
                elif(result.commandHitValue == CommandHitValues.PRUNE_PLAYLIST):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    permanentlyDelete = result.arguments[Main.commands.permanentlyDeleteFlag]
                    
                    for id in playlistIds:
                        Main.sharedCliController.prune(id, includeSoftDeleted, permanentlyDelete)
                
                elif(result.commandHitValue == CommandHitValues.PURGE_PLAYLIST):
                    Main.sharedCliController.purgePlaylists(True, True)

                elif(result.commandHitValue == CommandHitValues.PURGE):
                    Main.sharedCliController.purge()

                elif(result.commandHitValue == CommandHitValues.RESET_PLAYLIST_FETCH):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    
                    Main.playlistCliController.resetPlaylists(playlistIds)

        #         elif(arg in Main.commands.playCommands):
        #             # Expected input: playlistId or index, startIndex, shuffle, repeat
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(), Main.playlistService.getAllSorted(), 1, startAtZero = False, debug = Main.settings.debug)
        #             startIndex = int(inputArgs[1]) - 1 if(len(inputArgs) > 1) else 0
        #             shuffle = eval(inputArgs[2]) if(len(inputArgs) > 2) else False
        #             repeat = eval(inputArgs[3]) if(len(inputArgs) > 3) else False
                    
        #             Main.playlistCliController.playPlaylists(getIfExists(playlistIds, 0), startIndex, shuffle, repeat)

        #             argIndex += len(inputArgs) + 1
        #             continue

        #         elif(arg in Main.commands.downloadPlaylistCommands):
        #             # Expected input: playlistId or index, directoryName?, startIndex?, endIndex?, streamNameRegex?, useIndex?
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(), Main.playlistService.getAllSorted(), 1, startAtZero = False, debug = Main.settings.debug)
        #             directoryName = inputArgs[1] if(len(inputArgs) > 1) else None
        #             startIndex = int(inputArgs[2]) - 1 if(len(inputArgs) > 2) else None
        #             endIndex = int(inputArgs[3]) - 1 if(len(inputArgs) > 3) else None
        #             streamNameRegex = inputArgs[4] if(len(inputArgs) > 4) else None
        #             useIndex = eval(inputArgs[5]) if(len(inputArgs) > 5) else True
                    
        #             Main.playlistCliController.downloadPlaylist(getIfExists(playlistIds, 0), directoryName, startIndex, endIndex, streamNameRegex, useIndex)
                    
        #             argIndex += len(inputArgs) + 1
        #             continue

        #         elif(arg in Main.commands.exportPlaylistCommands):
        #             # Expected input: playlistId or index, directoryName?
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(), Main.playlistService.getAllSorted(), 1, startAtZero = False, debug = Main.settings.debug)
        #             directoryName = inputArgs[1] if(len(inputArgs) > 1) else None
                    
        #             Main.playlistCliController.exportPlaylist(getIfExists(playlistIds, 0), directoryName)
                    
        #             argIndex += len(inputArgs) + 1
        #             continue

        #         elif(arg in Main.commands.unwatchAllPlaylistCommands):
        #             # Expected input: playlistId or index
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(), Main.playlistService.getAllSorted(), 1, startAtZero = False, debug = Main.settings.debug)
                    
        #             Main.playlistCliController.unwatchAllInPlaylist(getIfExists(playlistIds, 0))
                    
        #             argIndex += len(inputArgs) + 1
        #             continue

        #         # Streams
        #         elif(arg in Main.commands.addStreamCommands):
        #             # Expected input: playlistId or index, uri, name?
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(), Main.playlistService.getAllSorted(), 1, startAtZero = False, setDefaultId = False, debug = Main.settings.debug)
        #             uri = inputArgs[1] if len(inputArgs) > 1 else None
        #             name = inputArgs[2] if len(inputArgs) > 2 else None
                    
        #             Main.queueStreamCliController.addQueueStream(getIfExists(playlistIds, 0), uri, name)

        #             argIndex += len(inputArgs) + 1
        #             continue

        #         # Streams
        #         elif(arg in Main.commands.addMultipleStreamsCommands):
        #             # Expected input: playlistId or index, uris
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(), Main.playlistService.getAllSorted(), 1, setDefaultId = False, startAtZero = False, debug = Main.settings.debug)
        #             uris = inputArgs[1:] if len(inputArgs) > 1 else None
                    
        #             Main.queueStreamCliController.addQueueStreams(getIfExists(playlistIds, 0), uris)

        #             argIndex += len(inputArgs) + 1
        #             continue

        #         elif(arg in Main.commands.deleteStreamCommands):
        #             # Expected input: playlistId or index, queueStreamIds or indices
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(), Main.playlistService.getAllSorted(), 1, setDefaultId = False, startAtZero = False, debug = Main.settings.debug)
        #             queueStreamIds = inputArgs[1:] if len(inputArgs) > 1 else []
                    
        #             Main.queueStreamCliController.deleteQueueStreams(getIfExists(playlistIds, 0), queueStreamIds)

        #             argIndex += len(inputArgs) + 1
        #             continue
                
        #         elif(arg in Main.commands.restoreStreamCommands):
        #             # Expected input: playlistId or index, queueStreamIds or indices
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(True), Main.playlistService.getAllSorted(True), 1, setDefaultId = False, startAtZero = False, debug = Main.settings.debug)
        #             queueStreamIds = inputArgs[1:] if len(inputArgs) > 1 else []
                                        
        #             Main.queueStreamCliController.restoreQueueStreams(getIfExists(playlistIds, 0), queueStreamIds)

        #             argIndex += len(inputArgs) + 1
        #             continue

        #         # Sources
        #         elif(arg in Main.commands.addSourcesCommands):
        #             # Expected input: playlistId or index, uri, enableFetch?, backgroundContent?, name?
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(), Main.playlistService.getAllSorted(), 1, startAtZero = False, debug = Main.settings.debug)
        #             uri = inputArgs[1] if len(inputArgs) > 1 else None
        #             enableFetch = eval(inputArgs[2]) if len(inputArgs) > 2 else True
        #             bgContent = eval(inputArgs[3]) if len(inputArgs) > 3 else False
        #             name = inputArgs[4] if len(inputArgs) > 4 else None
                    
        #             Main.streamSourceCliController.addStreamSource(getIfExists(playlistIds, 0), uri, enableFetch, bgContent, name)

        #             argIndex += len(inputArgs) + 1
        #             continue

        #         elif(arg in Main.commands.deleteSourceCommands):
        #             # Expected input: playlistId or index, streamSourceIds or indices
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(), Main.playlistService.getAllSorted(), 1, startAtZero = False, debug = Main.settings.debug)
        #             streamSourceIds = inputArgs[1:] if len(inputArgs) > 1 else []

        #             Main.streamSourceCliController.deleteStreamSources(getIfExists(playlistIds, 0), streamSourceIds)
                    
        #             argIndex += len(inputArgs) + 1
        #             continue
                
        #         elif(arg in Main.commands.restoreSourceCommands):
        #             # Expected input: playlistId or index, streamSourceIds or indices
        #             inputArgs = extractArgs(argIndex, argV)
        #             playlistIds = getIdsFromInput(inputArgs, Main.playlistService.getAllIdsSorted(True), Main.playlistService.getAllSorted(True), 1, startAtZero = False, debug = Main.settings.debug)
        #             streamSourceIds = inputArgs[1:] if len(inputArgs) > 1 else []
                    
        #             Main.streamSourceCliController.restoreStreamSources(getIfExists(playlistIds, 0), streamSourceIds)

        #             argIndex += len(inputArgs) + 1
        #             continue

        #         elif(arg in Main.commands.listSourcesCommands):
        #             # Expected input: includeSoftDeleted
        #             inputArgs = extractArgs(argIndex, argV)
        #             includeSoftDeleted = eval(inputArgs[0]) if(len(inputArgs) > 0) else False
                    
        #             Main.streamSourceCliController.listStreamSources(includeSoftDeleted)

        #             argIndex += len(inputArgs) + 1
        #             continue
                
        #         elif(arg in Main.commands.openSourceCommands):
        #             # Expected input: streamSourceIds or indices
        #             inputArgs = extractArgs(argIndex, argV)
        #             streamSourceIds = getIdsFromInput(inputArgs, Main.streamSourceService.getAllIds(), Main.streamSourceService.getAll(), startAtZero = False, debug = Main.settings.debug)
                    
        #             Main.streamSourceCliController.openStreamSource(streamSourceIds)

        #             argIndex += len(inputArgs) + 1
        #             continue

        #         # Meta
        #         elif(arg in Main.commands.listSettingsCommands):
        #             # Expected input: none
                    
        #             result = Main.settings.getAllSettingsAsTable()
        #             print(result)

        #             argIndex += 1
        #             continue
                
        #         elif(arg in Main.commands.listSoftDeletedCommands):
        #             # Expected input: simplified
        #             inputArgs = extractArgs(argIndex, argV)
        #             simplified = eval(inputArgs[0]) if(len(inputArgs) > 0) else False
                    
        #             result = Main.sharedService.getAllSoftDeleted()
        #             if(simplified):
        #                 resultList = [[e.summaryString() for e in l] for l in [*result.values()]]
        #             else: 
        #                 resultList = [[e.detailsString() for e in l] for l in [*result.values()]]
                        
        #             printLists(resultList, [*result.keys()])

        #             argIndex += len(inputArgs) + 1
        #             continue
                
        #         elif(arg in Main.commands.refactorCommands):
        #             # Expected input: None
                    
        #             refactorLastFetchedIdResult = Main.legacyService.refactorPlaytimeSecondsAlwaysDownloadFavorite()
        #             if(len(refactorLastFetchedIdResult) > 0):
        #                 printS("Refactored ", len(refactorLastFetchedIdResult), " StreamSources. IDs:", color = BashColor.OKGREEN)
        #                 printS(refactorLastFetchedIdResult)
        #             else:
        #                 printS("No refactors needed for refactorLastFetchedId.", color = BashColor.OKGREEN)

        #             argIndex += 1
        #             continue
                    
        except KeyboardInterrupt:
            printS("Program was aborted by user.", color = BashColor.OKGREEN)

if __name__ == "__main__":
    Main.main()
