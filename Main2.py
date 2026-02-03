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

        if(len(results) == 0):
            print("No valid command was found, please consult the manual for available commands. See the syntax description below:")
            print(argumentor.getSyntaxDescription())
            return
            
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

                elif(result.commandHitValue == CommandHitValues.DOWNLOAD_PLAYLIST):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    directoryName = result.arguments[Main.commands.directoryNameArgumentName]
                    startIndex = result.arguments[Main.commands.startIndexArgumentName]
                    endIndex = result.arguments[Main.commands.endIndexArgumentName]
                    streamNameRegex = result.arguments[Main.commands.streamNameRegexArgumentName]
                    useIndex = result.arguments[Main.commands.useIndexFlagName]
                    
                    Main.playlistCliController.downloadPlaylist(playlistIds[0], directoryName, startIndex, endIndex, streamNameRegex, useIndex)
                    
                elif(result.commandHitValue == CommandHitValues.EXPORT_PLAYLIST):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    directoryName = result.arguments[Main.commands.directoryNameArgumentName]
                    
                    Main.playlistCliController.exportPlaylist(playlistIds[0], directoryName)

                elif(result.commandHitValue == CommandHitValues.UNWATCH_ALL_PLAYLIST):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    
                    Main.playlistCliController.unwatchAllInPlaylist(playlistIds[0])

                # Playback
                elif(result.commandHitValue == CommandHitValues.PLAY):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    startIndex = result.arguments[Main.commands.startIndexArgumentName]
                    shuffle = result.arguments[Main.commands.shuffleFlagName]
                    repeat = result.arguments[Main.commands.repeatArguments]
                    
                    Main.playlistCliController.playPlaylists(playlistIds[0], startIndex, shuffle, repeat)

                # Streams
                elif(result.commandHitValue == CommandHitValues.ADD_STREAM):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    uris = result.arguments[Main.commands.uriArgumentName]
                    name = result.arguments[Main.commands.entityNameArgumentName]
                    
                    Main.queueStreamCliController.addQueueStream(playlistIds[0], uris[0], name)

                elif(result.commandHitValue == CommandHitValues.ADD_MULTIPLE_STREAMS):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    uris = result.arguments[Main.commands.uriArgumentName]
                    
                    Main.queueStreamCliController.addQueueStream(playlistIds[0], uris)

                elif(result.commandHitValue == CommandHitValues.DELETE_STREAM):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    queueStreamIds = result.arguments[Main.commands.queueStreamIdsArgument]
                    
                    Main.queueStreamCliController.deleteQueueStreams(playlistIds[0], queueStreamIds)
                
                elif(result.commandHitValue == CommandHitValues.RESTORE_STREAM):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    queueStreamIds = result.arguments[Main.commands.queueStreamIdsArgument]
                                        
                    Main.queueStreamCliController.restoreQueueStreams(playlistIds[0], queueStreamIds)

                # Sources
                elif(result.commandHitValue == CommandHitValues.ADD_SOURCE):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    uris = result.arguments[Main.commands.uriArgumentName]
                    enableFetch = result.arguments[Main.commands.enableFetchFlagName]
                    backgroundContent = result.arguments[Main.commands.backgroundContentFlagName]
                    name = result.arguments[Main.commands.entityNameArgumentName]
                    
                    ## TODO uris should be None of empty, or rewrite function to consider empty as none, but take first if any?
                    Main.streamSourceCliController.addStreamSource(playlistIds[0], uris[0], enableFetch, backgroundContent, name)

                elif(result.commandHitValue == CommandHitValues.DELETE_SOURCE):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    streamSourceIds = result.arguments[Main.commands.streamSourceIdsArgumentName]

                    Main.streamSourceCliController.deleteStreamSources(playlistIds[0], streamSourceIds)
                    
                elif(result.commandHitValue == CommandHitValues.RESTORE_SOURCE):
                    playlistIds = result.arguments[Main.commands.playlistIdsArgumentName]
                    streamSourceIds = result.arguments[Main.commands.streamSourceIdsArgumentName]
                    
                    Main.streamSourceCliController.restoreStreamSources(playlistIds[0], streamSourceIds)

                elif(result.commandHitValue == CommandHitValues.LIST_SOURCES):
                    includeSoftDeleted = result.arguments[Main.commands.includeSoftDeletedFlagName]
                    
                    Main.streamSourceCliController.listStreamSources(includeSoftDeleted)
                
                elif(result.commandHitValue == CommandHitValues.OPEN_SOURCE):
                    streamSourceIds = result.arguments[Main.commands.streamSourceIdsArgumentName]
                    
                    Main.streamSourceCliController.openStreamSource(streamSourceIds)

                # Meta
                elif(result.commandHitValue == CommandHitValues.LIST_SETTINGS):
                    result = Main.settings.getAllSettingsAsTable()
                    print(result)

                elif(result.commandHitValue == CommandHitValues.LIST_SOFT_DELETED):
                    simplified = result.arguments[Main.commands.simplifiedPrintFlagName]
                    
                    result = Main.sharedService.getAllSoftDeleted()
                    if(simplified):
                        resultList = [[e.summaryString() for e in l] for l in [*result.values()]]
                    else: 
                        resultList = [[e.detailsString() for e in l] for l in [*result.values()]]
                        
                    printLists(resultList, [*result.keys()])

                elif(result.commandHitValue == CommandHitValues.REFACTOR_OLD):
                    refactorLastFetchedIdResult = Main.legacyService.refactorPlaytimeSecondsAlwaysDownloadFavorite()
                    if(len(refactorLastFetchedIdResult) > 0):
                        printS("Refactored ", len(refactorLastFetchedIdResult), " StreamSources. IDs:", color = BashColor.OKGREEN)
                        printS(refactorLastFetchedIdResult)
                    else:
                        printS("No refactors needed for refactorLastFetchedId.", color = BashColor.OKGREEN)

        except KeyboardInterrupt:
            printS("Program was aborted by user.", color = BashColor.OKGREEN)

if __name__ == "__main__":
    Main.main()
