import os

import pytube
import validators
from grdException.ArgumentException import ArgumentException
from grdException.DatabaseException import DatabaseException
from grdException.NotFoundException import NotFoundException
from grdService.BaseService import BaseService
from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTime
from grdUtil.InputUtil import sanitize
from grdUtil.LocalJsonRepository import LocalJsonRepository
from grdUtil.LogLevel import LogLevel
from grdUtil.LogUtil import LogUtil
from grdUtil.PrintUtil import printD, printS
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource
from Settings import Settings

from services.QueueStreamService import QueueStreamService
from services.StreamSourceService import StreamSourceService

T = Playlist

class PlaylistService(BaseService[T]):
    settings: Settings = None
    playlistRepository: LocalJsonRepository = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    log: LogUtil = None

    def __init__(self):
        self.settings = Settings()
        self.queueStreamService = QueueStreamService()
        self.streamSourceService = StreamSourceService()
        self.log = LogUtil(self.settings.logDirPath, self.settings.debug, LogLevel.VERBOSE)
        
        BaseService.__init__(self, T, self.settings.debug, os.path.join(self.settings.localStoragePath, "Playlist"))

    def addStreams(self, playlistId: str, streams: list[QueueStream]) -> list[QueueStream]:
        """
        Add QueueStreams to Playlist.

        Args:
            playlistId (str): ID of Playlist to add to.
            streams (list[QueueStream]): QueueStreams to add.

        Returns:
            list[QueueStream]: QueueStreams added.
        """

        playlist = self.get(playlistId)
        if(playlist == None):
            self.log.logAsText(f"addStreams - Playlist with ID {playlistId} was not found.", logLevel = LogLevel.CRITICAL)
            raise NotFoundException(f"addStreams - Playlist with ID {playlistId} was not found.")

        playlistStreamUris = []
        playlistStreamNames = []
        if(not playlist.allowDuplicates):
            playlistStreams = self.getStreamsByPlaylistId(playlist.id)
            playlistStreamUris = [_.uri for _ in playlistStreams]
            playlistStreamNames = [_.name for _ in playlistStreams]
            
        added = []
        for stream in streams:            
            if(not playlist.allowDuplicates and (stream.uri in playlistStreamUris or stream.name in playlistStreamNames)):
                self.log.logAsText(f"addStreams - Attempted to add stream {stream.uri} but Playlist with ID {playlistId} does not allow duplicates.", logLevel = LogLevel.VERBOSE)
                printS("\"", stream.name, "\" / ", stream.uri, " already exists in Playlist \"", playlist.name, "\" and allow duplicates for this Playlist is disabled.", color = BashColor.WARNING)
                continue

            addResult = self.queueStreamService.add(stream)
            if(not addResult): # Will abort add if an entity already exists with that ID
                self.log.logAsText(f"addStreams - Failed to add streams to Playlist {playlist.name}, ID: {playlist.id}.", logLevel = LogLevel.CRITICAL)
                raise DatabaseException(f"addStreams - Failed to add streams to Playlist {playlist.name}, ID: {playlist.id}.")
            
            playlist.streamIds.append(stream.id)
            added.append(addResult)

        playlist.updated = getDateTime()
        updateResult = self.update(playlist)
        if(len(added) > 0 and updateResult != None):
            return added
        else:
            self.log.logAsText(f"addStreams - No streams added and updateResult failed, removing potentially added QueueStreams.", logLevel = LogLevel.CRITICAL)
            # Delete added QueueStreams if update of Playlist failed
            for stream in added:
                self.queueStreamService.remove(stream.id, includeSoftDeleted = True)
            
            return []

    def deleteStreams(self, playlistId: str, streamIds: list[str], includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> list[QueueStream]:
        """
        (Soft) Delete/remove QueueStreams from Playlist.

        Args:
            playlistId (str): ID of Playlist to remove from.
            streamIds (list[str]): IDs of QueueStreams to remove.
            includeSoftDeleted (bool, optional): Should include soft-deleted entities. Defaults to False.
            permanentlyDelete (bool, optional): Should entities be permanently deleted. Defaults to False.

        Returns:
            list[QueueStream]: QueueStreams deleted/removed.
        """

        result = []
        playlist = self.get(playlistId, includeSoftDeleted)
        if(playlist == None):
            self.log.logAsText(f"deleteStreams - Playlist with ID {playlistId} was not found.", logLevel = LogLevel.CRITICAL)
            raise NotFoundException(f"deleteStreams - Playlist with ID {playlistId} was not found.")

        for id in streamIds:
            stream = self.queueStreamService.get(id, includeSoftDeleted)
            if(stream == None):
                self.log.logAsText("deleteStreams - Continued loop, stream == None. id: ", id, logLevel = LogLevel.INFO)
                continue
            
            removeResult = None
            if(permanentlyDelete):
                self.log.logAsText("deleteStreams - Remove. id: ", id, logLevel = LogLevel.INFO)
                removeResult = self.queueStreamService.remove(id, includeSoftDeleted)
            else:
                self.log.logAsText("deleteStreams - Delete. id: ", id, logLevel = LogLevel.INFO)
                removeResult = self.queueStreamService.delete(id)
            if(removeResult != None):
                playlist.streamIds.remove(stream.id)
                result.append(stream)

        updateResult = self.update(playlist)
        if(updateResult != None):
            return result
        else:
            self.log.logAsText("deleteStreams failed, updateResult None. PlaylistId: ", playlistId, "  streamIds: ", streamIds, logLevel = LogLevel.ERROR)
            return []
        
    def restoreStreams(self, playlistId: str, streamIds: list[str]) -> list[QueueStream]:
        """
        Restore QueueStreams to Playlist.

        Args:
            playlistId (str): ID of Playlist to restore to.
            streamIds (list[str]): IDs of QueueStreams to restore.

        Returns:
            list[QueueStream]: QueueStreams restored.
        """

        result = []
        playlist = self.get(playlistId, includeSoftDeleted = True)
        if(playlist == None):
            raise NotFoundException(f"restoreStreams - Playlist with ID {playlistId} was not found.")

        for id in streamIds:
            stream = self.queueStreamService.get(id, includeSoftDeleted = True)
            if(stream == None):
                continue
            
            restoreResult = self.queueStreamService.restore(id)
            if(restoreResult != None):
                playlist.streamIds.append(stream.id)
                result.append(stream)

        updateResult = self.update(playlist)
        if(updateResult):
            return result
        else:
            return []

    def moveStream(self, playlistId: str, fromIndex: int, toIndex: int) -> bool:
        """
        Move streams internally in Playlist, by index.

        Args:
            playlistId (str): ID of Playlist to move in.
            fromIndex (int): index move.
            toIndex (int): index to move to.

        Returns:
            bool: Result.
        """

        playlist = self.get(playlistId)
        if(playlist == None):
            raise NotFoundException(f"moveStream - Playlist with ID {playlistId} was not found.")

        listLength = len(playlist.streamIds)
        if(fromIndex == toIndex):
            printD("Index from and to were the same. No update needed.", color=BashColor.WARNING, debug = self.settings.debug)
            return True
        if(fromIndex < 0 or fromIndex >= listLength):
            printS("Index to move from (", fromIndex, ") was out or range.", color=BashColor.WARNING)
            return False
        if(toIndex < 0 or toIndex >= listLength):
            printS("Index to move to (", toIndex, ") was out or range.", color=BashColor.WARNING)
            return False

        ## TODO check before/after and how stuff moves?
        entry = playlist.streamIds[fromIndex]
        playlist.streamIds.pop(fromIndex)
        playlist.streamIds.insert(toIndex, entry)

        playlist.updated = getDateTime()
        return self.update(playlist)
    
    def addStreamSources(self, playlistId: str, streamSources: list[StreamSource]) -> list[StreamSource]:
        """
        Add StreamSources to Playlist.

        Args:
            playlistId (str): ID of Playlist to add to.
            streamSources (list[StreamSource]): StreamSources to add.

        Returns:
            list[StreamSource]: StreamSources added.
        """

        playlist = self.get(playlistId)
        if(playlist == None):
            raise NotFoundException(f"addStreamSources - Playlist with ID {playlistId} was not found.")

        playlistStreamSourceUris = []
        playlistStreamSourceNames = []
        if(not playlist.allowDuplicates):
            playlistStreams = self.getSourcesByPlaylistId(playlist.id)
            playlistStreamSourceUris = [_.uri for _ in playlistStreams]
            playlistStreamSourceNames = [_.name for _ in playlistStreams]
            
        added = []
        for source in streamSources:
            if(not playlist.allowDuplicates and (source.uri in playlistStreamSourceUris or source.name in playlistStreamSourceNames)):
                printS("\"", source.name, "\" / ", source.uri, " already exists in Playlist \"", playlist.name, "\" and allow duplicates for this Playlist is disabled.", color = BashColor.WARNING)
                continue

            addResult = self.streamSourceService.add(source)            
            if(addResult == None):
                printS("\"", source.name, "\" could not be added.", color = BashColor.FAIL)
                continue

            playlist.streamSourceIds.append(source.id)
            added.append(addResult)

        playlist.updated = getDateTime()
        updateResult = self.update(playlist)
        if(len(added) > 0 and updateResult != None):
            return added
        else:
            # Delete added StreamSources if update of Playlist failed
            for source in added:
                self.streamSourceService.remove(source.id, includeSoftDeleted = True)
            return []
    
    def deleteStreamSources(self, playlistId: str, streamSourceIds: list[str]) -> list[StreamSource]:
        """
        (Soft) Delete StreamSources from Playlist.

        Args:
            playlistId (str): ID of Playlist to delete from.
            streamSourceIds (list[str]): IDs of StreamSources to delete.

        Returns:
            list[StreamSource]: StreamSources deleted.
        """

        result = []
        playlist = self.get(playlistId)
        if(playlist == None):
            raise NotFoundException(f"deleteStreamSources - Playlist with ID {playlistId} was not found.")

        for id in streamSourceIds:
            source = self.streamSourceService.get(id)
            if(source == None):
                continue
            
            removeResult = self.streamSourceService.delete(id)
            if(removeResult != None):
                playlist.streamSourceIds.remove(source.id)
                result.append(source)

        updateResult = self.update(playlist)
        if(updateResult):
            return result
        else:
            return []
        
    def restoreStreamSources(self, playlistId: str, streamSourceIds: list[str]) -> list[StreamSource]:
        """
        Restore StreamSources to Playlist.

        Args:
            playlistId (str): ID of Playlist to restore to.
            streamSourceIds (list[str]): IDs of StreamSources to restore.

        Returns:
            list[StreamSource]: StreamSource restored.
        """

        result = []
        playlist = self.get(playlistId, includeSoftDeleted = True)
        if(playlist == None):
            raise NotFoundException(f"restoreStreamSources - Playlist with ID {playlistId} was not found.")

        for id in streamSourceIds:
            source = self.streamSourceService.get(id, includeSoftDeleted = True)
            if(source == None):
                continue
            
            restoreResult = self.streamSourceService.restore(id)
            if(restoreResult != None):
                playlist.streamSourceIds.append(source.id)
                result.append(source)

        updateResult = self.update(playlist)
        if(updateResult):
            return result
        else:
            return []

    def getStreamsByPlaylistId(self, playlistId: str, includeSoftDeleted: bool = False) -> list[QueueStream]:
        """
        Get all QueueStreams in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to add to.
            includeSoftDeleted (bool): should include soft-deleted entities.

        Returns:
            list[QueueStream]: QueueStreams if any, else empty list.
        """

        playlist = self.get(playlistId, includeSoftDeleted)
        if(playlist == None):
            raise NotFoundException(f"getStreamsByPlaylistId - Playlist with ID {playlistId} was not found.")

        playlistStreams = []
        for id in playlist.streamIds:
            stream = self.queueStreamService.get(id, includeSoftDeleted)
            if(stream == None):
                printS("A QueueStream with ID: ", id, " was listed in Playlist \"", playlist.name, "\", but was not found in the database. Consider removing it by running the purge command.", color = BashColor.WARNING)
                continue
            
            playlistStreams.append(stream)

        return playlistStreams
    
    def getUnwatchedStreamsByPlaylistId(self, playlistId: str, includeSoftDeleted: bool = False) -> list[QueueStream]:
        """
        Get unwatched QueueStreams in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to get from.
            includeSoftDeleted (bool): should include soft-deleted entities.

        Returns:
            list[QueueStream]: QueueStreams if any, else empty list.
        """

        playlist = self.get(playlistId, includeSoftDeleted)
        if(playlist == None):
            raise NotFoundException(f"getUnwatchedStreamsByPlaylistId - Playlist with ID {playlistId} was not found.")

        playlistStreams = []
        for id in playlist.streamIds:
            stream = self.queueStreamService.get(id, includeSoftDeleted)
            if(stream == None):
                printS("A QueueStream with ID: ", id, " was listed in Playlist \"", playlist.name, "\", but was not found in the database. Consider removing it by running the purge command.", color = BashColor.WARNING)
                continue
            
            if(stream.watched == None):
                playlistStreams.append(stream)

        return playlistStreams    
    
    def getSourcesByPlaylistId(self, playlistId: str, getFetchEnabledOnly: bool = False, includeSoftDeleted: bool = False) -> list[StreamSource]:
        """
        Get StreamSources in playlist from playlistId.

        Args:
            playlistId (str): ID of playlist to get from.
            includeSoftDeleted (bool): should include soft-deleted entities.

        Returns:
            list[StreamSource]: StreamSources if any, else empty list.
        """

        playlist = self.get(playlistId, includeSoftDeleted)
        if(playlist == None):
            raise NotFoundException(f"getSourcesByPlaylistId - Playlist with ID {playlistId} was not found.")

        playlistSources = []
        for id in playlist.streamSourceIds:
            source = self.streamSourceService.get(id, includeSoftDeleted)
            if(source == None):
                printS("A StreamSource with ID: ", id, " was listed in Playlist \"", playlist.name, "\", but was not found in the database. Consider removing it by running the purge command.", color = BashColor.WARNING)
                continue
            
            if(getFetchEnabledOnly and not source.enableFetch):
                continue
                
            playlistSources.append(source)

        return playlistSources

    def addYouTubePlaylist(self, playlist: Playlist, url: str) -> T:
        """
        Create a Playlist, using a YouTube playlist as the starting point. Videos will be added as streams in the playlist TODO? and source will be the playlist.

        Args:
            playlist (Playlist): Playlist to save to.
            url (str): URI to YouTube playlist.

        Returns:
            Playlist: Playlist if created, else None.
        """
        
        if(playlist == None):
            raise ArgumentException(f"addYouTubePlaylist - playlist was None.")
        
        if(not validators.url(url)):
            raise ArgumentException(f"addYouTubePlaylist - URL \"", url, "\" was not an accepted, absolute URL.")
        
        ytPlaylist = pytube.Playlist(url)
        try:
            # For some reasons the property call just fails for invalid playlist, instead of being None. Except = fail.
            ytPlaylist.title == None
        except:
            raise ArgumentException(f"addYouTubePlaylist - YouTube playlist given by URL \"", url, "\" was not found. It could be set to private or deleted")
        
        if(playlist.name == None):
            playlist.name = sanitize(ytPlaylist.title)
        if(playlist.description == None):
            playlist.description = f"Playlist created from YouTube playlist: {url}"
        
        streamsToAdd = []
        for videoUrl in ytPlaylist.video_urls:
            video = pytube.YouTube(videoUrl)
            stream = QueueStream(name = sanitize(video.title), uri = video.watch_url)
            streamsToAdd.append(stream)
        
        addPlaylistResult = self.add(playlist)
        if(addPlaylistResult != None):
            addStreamsResult = self.addStreams(addPlaylistResult.id, streamsToAdd)
            if(len(addStreamsResult) > 0):
                return addPlaylistResult
            
        return None
    
    def printPlaylistDetails(self, playlistIds: list[str], includeUri: bool = False, includeId: bool = False, includeDatetime: bool = False, includeListCount: bool = False, includeSource: bool = True) -> int:
        """
        Print detailed info for Playlist, including details for related StreamSources and QueueStreams.

        Args:
            playlistIds (list[str]): list of playlistIds to print details of.
            includeUri (bool, optional): should print include URI if any. Defaults to False.
            includeId (bool, optional): should print include IDs. Defaults to False.
            includeSource (bool, optional): should print include StreamSource this was fetched from. Defaults to True.
            
        Returns:
            int: number of playlists printed for.
        """
        
        includeSoftDeleted = True
        result = 0
        for id in playlistIds:
            playlist = self.get(id, includeSoftDeleted)
              
            playlistDetailsString = playlist.detailsString(includeUri, includeId, includeDatetime, includeListCount = False)
            if(includeListCount):
                unwatchedStreams = self.getUnwatchedStreamsByPlaylistId(playlist.id)
                fetchedSources = self.getSourcesByPlaylistId(playlist.id, getFetchEnabledOnly = True)
                sourcesListString = f", unwatched streams: {len(unwatchedStreams)}/{len(playlist.streamIds)}"
                streamsListString = f", fetched sources: {len(fetchedSources)}/{len(playlist.streamSourceIds)}"
                playlistDetailsString += sourcesListString + streamsListString

            printS(playlistDetailsString)
            
            printS("\tStreamSources", color = BashColor.BOLD)
            if(len(playlist.streamSourceIds) == 0):
                printS("\tNo sources added yet.")
            
            for i, sourceId in enumerate(playlist.streamSourceIds):
                source = self.streamSourceService.get(sourceId, includeSoftDeleted)
                if(source == None):
                    printS("\tStreamSource not found (ID: \"", sourceId, "\").", color = BashColor.FAIL)
                    continue
                
                color = "WHITE" if i % 2 == 0 else "GREYBG"
                printS("\t", str(i), " - ", source.detailsString(includeUri, includeId, includeDatetime, includeListCount), color = BashColor[color])
            
            print("\n")
            printS("\tQueueStreams", color = BashColor.BOLD)
            if(len(playlist.streamIds) == 0):
                printS("\tNo streams added yet.")
            
            for i, streamId in enumerate(playlist.streamIds):
                stream = self.queueStreamService.get(streamId, includeSoftDeleted)
                if(stream == None):
                    printS("\tQueueStream not found (ID: \"", streamId, "\").", color = BashColor.FAIL)
                    continue
                
                color = "WHITE" if i % 2 == 0 else "GREYBG"
                sourceString = ""
                if(includeSource and stream.streamSourceId != None):
                    streamSource = self.streamSourceService.get(stream.streamSourceId, includeSoftDeleted)
                    
                    if(streamSource == None):
                        printS("\tStreamSource not found (ID: \"", streamId, "\").", color = BashColor.FAIL)
                        continue
                    
                    sourceString = ", StreamSource: \"" + streamSource.name + "\"" 
                printS("\t", str(i), " - ", stream.detailsString(includeUri, includeId, includeDatetime, includeListCount), sourceString, color = BashColor[color])
                
            result += 1
                
        return result
