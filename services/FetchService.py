import sys
from datetime import datetime
from typing import Dict, List, Tuple
from xml.dom.minidom import parseString

import requests
from enums.StreamSourceType import StreamSourceType
from grdException.ArgumentException import ArgumentException
from grdException.DatabaseException import DatabaseException
from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTime, stringToDatetime
from grdUtil.FileUtil import mkdir
from grdUtil.InputUtil import sanitize
from grdUtil.PrintUtil import printD, printS
from model.OdyseeStream import OdyseeStream
from model.Playlist import Playlist
from model.PlaylistDetailed import PlaylistDetailed
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource
from pytube import Channel
from Settings import Settings

from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.StreamSourceService import StreamSourceService


class FetchService():
    settings: Settings = None
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None

    def __init__(self):
        self.settings = Settings()
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.streamSourceService = StreamSourceService()

        mkdir(self.settings.localStoragePath)

    def fetch(self, playlistId: str, batchSize: int = 10, takeAfter: datetime = None, takeBefore: datetime = None, takeNewOnly: bool = False) -> int:
        """
        Fetch new videos from watched sources, adding them in chronological order.

        Args:
            batchSize (int): Number of videos to check at a time, unrelated to max videos that will be read. Defaults to 10.
            takeAfter (datetime): Limit to take video after. Defaults to None.
            takeBefore (datetime): Limit to take video before. Defaults to None.
            takeNewOnly (bool): Only take streams marked as new. Disables takeAfter and takeBefore-checks. To use takeAfter and/or takeBefore, set this to False. Defaults to False.

        Returns:
            int: Number of videos added.
        """
        
        if(batchSize < 1):
            raise ArgumentException("fetch - batchSize was less than 1.")

        playlist = self.playlistService.get(playlistId)
        if(playlist == None):
            return 0

        newStreams = []
        for sourceId in playlist.streamSourceIds:
            source = self.streamSourceService.get(sourceId)
            
            if(source == None):
                printS("StreamSource with ID ", sourceId, " could not be found. Consider removing it using the purge or purgeplaylists commands.", color = BashColor.FAIL)
                continue
            
            if(not source.enableFetch):
                continue

            fetchedStreams = []
            _takeAfter = takeAfter if(not takeNewOnly) else source.lastSuccessfulFetched
            
            if(source.isWeb):
                if(source.streamSourceTypeId == StreamSourceType.YOUTUBE.value):
                    fetchedStreams = self.fetchYoutube(source, batchSize, _takeAfter, takeBefore, takeNewOnly)
                elif(source.streamSourceTypeId == StreamSourceType.ODYSEE.value):
                    fetchedStreams = self.fetchOdysee(source, batchSize, _takeAfter, takeBefore, takeNewOnly)
                else:
                    printS("\t Source \"", source.name, "\" could not be fetched as it is not implemented for this source.", color = BashColor.WARNING)
                    continue
            else:
                fetchedStreams = self.fetchDirectory(source, batchSize, _takeAfter, takeBefore, takeNewOnly)

            if(len(fetchedStreams) > 0):
                source.lastSuccessfulFetched = getDateTime()
            
            source.lastFetchedIds = fetchedStreams[1]
            source.lastFetched = getDateTime()
            updateSuccess = self.streamSourceService.update(source)
            if(updateSuccess):
                newStreams += fetchedStreams[0]
            else:
                printS("Could not update StreamSource \"", source.name, "\" (ID: ", source.id, "), streams could not be added: \n", fetchedStreams, color = BashColor.WARNING)
                
            sys.stdout.flush()

        updateResult = self.playlistService.addStreams(playlist.id, newStreams)
        if(len(updateResult) > 0):
            return len(newStreams)
        else:
            return 0

    def fetchDirectory(self, streamSource: StreamSource, batchSize: int = 10, takeAfter: datetime = None, takeBefore: datetime = None, takeNewOnly: bool = False) -> Tuple[List[QueueStream], str]:
        """
        Fetch streams from a local directory.

        Args:
            batchSize (int): Number of videos to check at a time, unrelated to max videos that will be read. Defaults to 10.
            takeAfter (datetime): Limit to take video after. Defaults to None.
            takeBefore (datetime): Limit to take video before. Defaults to None.
            takeNewOnly (bool): Only take streams marked as new. Disables takeAfter and takeBefore-checks. To use takeAfter and/or takeBefore, set this to False. Defaults to False.

        Returns:
            Tuple[List[QueueStream], str]: A Tuple of List of QueueStream, and the last filename fetched.
        """
        
        if(streamSource == None):
            raise ArgumentException("fetchDirectory - streamSource was None")

        emptyReturn = ([], streamSource.lastFetchedIds)
        return emptyReturn

    def fetchYoutube(self, streamSource: StreamSource, batchSize: int = 10, takeAfter: datetime = None, takeBefore: datetime = None, takeNewOnly: bool = False) -> Tuple[List[QueueStream], List[str]]:
        """
        Fetch videos from YouTube.

        Args:
            batchSize (int): Number of videos to check at a time, unrelated to max videos that will be read. Defaults to 10.
            takeAfter (datetime): Limit to take video after. Defaults to None.
            takeBefore (datetime): Limit to take video before. Defaults to None.
            takeNewOnly (bool): Only take streams marked as new. Disables takeAfter and takeBefore-checks. To use takeAfter and/or takeBefore, set this to False. Defaults to False.

        Returns:
            Tuple[List[QueueStream], List[str]]: A Tuple of List of QueueStream, and List of last YouTube IDs fetched.
        """
        
        if(streamSource == None):
            raise ArgumentException("fetchYoutube - streamSource was None.")

        emptyReturn = ([], streamSource.lastFetchedIds)
        channel = Channel(streamSource.uri)

        if(channel == None or channel.channel_name == None):
            printS(f"Channel {streamSource.name} (URL: {streamSource.uri}) could not be found or is not valid. Please remove it and add it back.", color = BashColor.FAIL)
            return emptyReturn

        printS(f"Fetching videos from {channel.channel_name}...")
        sys.stdout.flush()
        if(len(channel.video_urls) < 1):
            printS(f"Channel {channel.channel_name} has no videos.", color = BashColor.WARNING)
            return emptyReturn

        newStreams = []
        newQueueStreams = []
        streams = List(channel.videos)
        lastStreamId = streams[0].video_id
        if(takeNewOnly and takeAfter == None and lastStreamId in streamSource.lastFetchedIds):
            printD("Last video fetched: \"", sanitize(streams[0].title), "\", YouTube ID \"", lastStreamId, "\"", color = BashColor.WARNING, debug = self.settings.debug)
            printD("Return due to takeNewOnly and takeAfter == None and lastStreamId in streamSource.lastFetchedIds", color = BashColor.WARNING, debug = self.settings.debug)
            return emptyReturn
            
        for i, stream in enumerate(streams):
            if(takeNewOnly and stream.video_id in streamSource.lastFetchedIds):
                printD("Name \"", sanitize(stream.title), "\", YouTube ID \"", stream.video_id, "\"", color = BashColor.WARNING, debug = self.settings.debug)
                printD("Break due to takeNewOnly and stream.video_id in streamSource.lastFetchedIds", color = BashColor.WARNING, debug = self.settings.debug)
                break
            elif(not takeNewOnly and takeAfter != None and stream.publish_date < takeAfter):
                printD("Break due to not takeNewOnly and takeAfter != None and stream.publish_date < takeAfter", color = BashColor.WARNING, debug = self.settings.debug)
                break
            elif(not takeNewOnly and takeBefore != None and stream.publish_date > takeBefore):
                printD("Continue due to not takeNewOnly and takeBefore != None and stream.publish_date > takeBefore", color = BashColor.WARNING, debug = self.settings.debug)
                continue
            elif(i > batchSize):
                printD("Break due to i > batchSize", color = BashColor.WARNING, debug = self.settings.debug)
                break
            
            newStreams.append(stream)
            
        if(len(newStreams) == 0):
            return emptyReturn
        
        newStreams.reverse()
        for stream in newStreams:
            sanitizedTitle = sanitize(stream.title)
            printS("\tAdding \"", sanitizedTitle, "\".")
            queueStream = QueueStream(name = sanitizedTitle, 
                uri = stream.watch_url, 
                isWeb = True,
                streamSourceId = streamSource.id,
                watched = None,
                backgroundContent = streamSource.backgroundContent,
                added = getDateTime())
            
            newQueueStreams.append(queueStream)
            
        streamSource.lastFetchedIds.append(lastStreamId)
        if(len(streamSource.lastFetchedIds) > batchSize):
            streamSource.lastFetchedIds.pop(0)
        
        return (newQueueStreams, streamSource.lastFetchedIds)
    
    def fetchOdysee(self, streamSource: StreamSource, batchSize: int = 10, takeAfter: datetime = None, takeBefore: datetime = None, takeNewOnly: bool = False) -> Tuple[List[QueueStream], List[str]]:
        """
        Fetch videos from Odysee.

        Args:
            batchSize (int): Number of videos to check at a time, unrelated to max videos that will be read. Defaults to 10.
            takeAfter (datetime): Limit to take video after. Defaults to None.
            takeBefore (datetime): Limit to take video before. Defaults to None.
            takeNewOnly (bool): Only take streams marked as new. Disables takeAfter and takeBefore-checks. To use takeAfter and/or takeBefore, set this to False. Defaults to False.

        Returns:
            Tuple[List[QueueStream], List[str]]: A Tuple of List of QueueStream, and List of last Odysee IDs fetched.
        """
        
        if(streamSource == None):
            raise ArgumentException("fetchOdysee - streamSource was None.")

        emptyReturn = ([], streamSource.lastFetchedIds)
        channelName = "".join(["@", streamSource.uri.split("@")[-1]])
        rssUri = f"https://odysee.com/$/rss/{channelName}"
        rssRequest = requests.get(rssUri)
        xml = rssRequest.content
        document = None
        
        if(rssRequest.status_code != 200): # TODO code might be 200 with empty content or "oops nothing here". Test when Odysee is down next and update this
            printS("Channel \"", streamSource.name, "\" (URL: ", streamSource.uri, ") could not be fetched, the connection likely timed out. Try again later", color = BashColor.WARNING)
            return emptyReturn
        
        try:
            document = parseString(xml)
        except:
            printS("Channel \"", streamSource.name, "\" (URL: ", streamSource.uri, ") could not be found or is not valid. Please remove it and add it back.", color = BashColor.FAIL)
            return emptyReturn

        streams = document.getElementsByTagName("item")
        printS(f"Fetching videos from {streamSource.name}...")
        sys.stdout.flush()
        if(len(streams) < 1):
            printS(f"Channel {streamSource.name} has no videos.", color = BashColor.WARNING)
            return emptyReturn

        newStreams = []
        newQueueStreams = []
        lastStreamTitle = sanitize(streams[0].getElementsByTagName("title")[0].firstChild.nodeValue)
        lastStreamId = streams[0].getElementsByTagName("link")[0].firstChild.nodeValue.split(":")[-1]
        if(takeNewOnly and takeAfter == None and lastStreamId in streamSource.lastFetchedIds):
            printD("Last video fetched: \"", lastStreamTitle, "\", Odysee ID \"", lastStreamId, "\"", color = BashColor.WARNING, debug = self.settings.debug)
            printD("Return due to takeNewOnly and takeAfter == None and lastStreamId in streamSource.lastFetchedIds", color = BashColor.WARNING, debug = self.settings.debug)
            return emptyReturn
        
        for i, stream in enumerate(streams):
            title = sanitize(stream.getElementsByTagName("title")[0].firstChild.nodeValue)
            pubDateRaw = stream.getElementsByTagName("pubDate")[0].firstChild.nodeValue
            pubDate = stringToDatetime(pubDateRaw, "%a, %d %b %Y %H:%M:%S %Z") #Mon, 07 Jun 2021 04:57:59 GMT
            link = stream.getElementsByTagName("link")[0].firstChild.nodeValue
            videoGuid = link.split(":")[-1]
            
            if(takeNewOnly and videoGuid in streamSource.lastFetchedIds):
                printD("Name \"", title, "\", Odysee ID \"", videoGuid, "\"", color = BashColor.WARNING, debug = self.settings.debug)
                printD("Break due to takeNewOnly and videoGuid in streamSource.lastFetchedIds", color = BashColor.WARNING, debug = self.settings.debug)
                break
            elif(not takeNewOnly and takeAfter != None and pubDate < takeAfter):
                printD("Break due to not takeNewOnly and takeAfter != None and pubDate < takeAfter", color = BashColor.WARNING, debug = self.settings.debug)
                break
            elif(not takeNewOnly and takeBefore != None and pubDate > takeBefore):
                printD("Continue due to not takeNewOnly and takeBefore != None and pubDate > takeBefore", color = BashColor.WARNING, debug = self.settings.debug)
                continue
            elif(i > batchSize):
                printD("Beak due to i > batchSize", color = BashColor.WARNING, debug = self.settings.debug)
                break
            
            newStreams.append(OdyseeStream(title, pubDate, link, videoGuid))
            
        if(len(newStreams) == 0):
            return emptyReturn
        
        newStreams.reverse()
        for stream in newStreams:
            printS("\tAdding \"", stream.title, "\".")
            queueStream = QueueStream(name = stream.title, 
                uri = stream.link, 
                isWeb = True,
                streamSourceId = streamSource.id,
                watched = None,
                backgroundContent = streamSource.backgroundContent,
                added = getDateTime())
            
            newQueueStreams.append(queueStream)
            
        streamSource.lastFetchedIds.append(lastStreamId)
        if(len(streamSource.lastFetchedIds) > batchSize):
            streamSource.lastFetchedIds.pop(0)
        
        return (newQueueStreams, streamSource.lastFetchedIds)
    
    def resetPlaylistFetch(self, playlistIds: List[str]) -> int:
        """
        Reset the fetch-status for sources of a playlist and deletes all streams.

        Args:
            playlistIds (List[str]): List of playlistIds.
            
        Returns:
            int: Number of playlists reset.
        """
        
        result = 0
        for playlistId in playlistIds:            
            playlist = self.playlistService.get(playlistId)
            deleteUpdateResult = True
            
            for queueStreamId in playlist.streamIds:
                deleteStreamResult = self.queueStreamService.delete(queueStreamId)
                deleteUpdateResult = deleteUpdateResult and deleteStreamResult != None
            
            playlist.streamIds = []
            updateplaylistResult = self.playlistService.update(playlist)
            deleteUpdateResult = deleteUpdateResult and updateplaylistResult != None
            
            for streamSourceId in playlist.streamSourceIds:
                streamSource = self.streamSourceService.get(streamSourceId)
                streamSource.lastFetched = None
                updateStreamResult = self.streamSourceService.update(streamSource)
                deleteUpdateResult = deleteUpdateResult and updateStreamResult != None
            
            if(deleteUpdateResult):
                result += 1
                
        return result
    
    def prepareReset(self, playlistId: str, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> PlaylistDetailed:
        """
        Prepare to reset the fetch-status for StreamSources of Playlist given by data and deletes all QueueStreams in it.

        Args:
            playlistId (str): ID of Playlist to reset.
            includeSoftDeleted (bool, optional): Should include soft-deleted entities. Defaults to False.
            permanentlyDelete (bool, optional): Should entities be permanently deleted. Defaults to False.
            
        Returns:
            DPlaylistDetailed: Entities to reset.
        """
        
        if(not playlistId):
            raise ArgumentException(f"prepareReset - missing playlistId.")
        
        dataEmpty = {"QueueStream": [], "StreamSource": [], "Playlist": None}
        data = dataEmpty.copy()
        
        playlist = self.playlistService.get(playlistId, includeSoftDeleted)        
        return PlaylistDetailed(playlist, [], []) # TODO get all by ids
    
    def doReset(self, data: PlaylistDetailed, includeSoftDeleted: bool = False, permanentlyDelete: bool = False) -> Playlist:
        """
        Reset the fetch-status for StreamSources of Playlist given by data and deletes all QueueStreams in it.

        Args:
            data (PlaylistDetailed): Data to reset.
            includeSoftDeleted (bool, optional): Should include soft-deleted entities. Defaults to False.
            permanentlyDelete (bool, optional): Should entities be permanently deleted. Defaults to False.
            
        Returns:
            Playlist: Result.
        """
        
        if(not data.playlist or not data.playlist.id):
            raise ArgumentException(f"doReset - missing Playlist data or Playlist ID.")
        
        playlist = self.playlistService.get(data.playlist.id, includeSoftDeleted)
        
        deleteResult = self.playlistService.deleteStreams(playlist.id, playlist.streamIds, includeSoftDeleted, permanentlyDelete)
        if(not deleteResult):
            raise DatabaseException(f"doReset - failed to update Playlist {playlist.name} with id {playlist.id}.")
        
        for id in playlist.streamSourceIds:
            entity = self.streamSourceService.get(id, includeSoftDeleted)
            entity.lastFetched = None
            entity.lastFetchedIds = []
            updateResult = self.streamSourceService.update(entity)
            if(not updateResult):
                raise DatabaseException(f"doReset - failed to update StreamSource {entity.name} with id {entity.id}.")
        
        return self.playlistService.get(playlist.id, includeSoftDeleted)   
