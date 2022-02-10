import os
import sys
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from myutil.BashColor import BashColor
from myutil.DateTimeObject import DateTimeObject
from myutil.FileUtil import mkdir
from myutil.InputUtil import sanitize
from myutil.PrintUtil import printS
from pytube import Channel

from enums.StreamSourceType import StreamSourceType
from model.QueueStream import QueueStream
from model.StreamSource import StreamSource
from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService
from StreamSourceService import StreamSourceService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

class FetchService():
    storagePath: str = LOCAL_STORAGE_PATH
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None

    def __init__(self):
        self.playlistService: PlaylistService = PlaylistService()
        self.queueStreamService: QueueStreamService = QueueStreamService()
        self.streamSourceService: StreamSourceService = StreamSourceService()

        mkdir(self.storagePath)

    def fetch(self, playlistId: str, batchSize: int = 10, takeAfter: datetime = None, takeBefore: datetime = None) -> int:
        """
        Fetch new videos from watched sources, adding them in chronological order.

        Args:
            batchSize (int): number of videos to check at a time, unrelated to max videos that will be read
            takeAfter (datetime): limit to take video after
            takeBefore (datetime): limit to take video before

        Returns:
            int: number of videos added
        """

        _playlist = self.playlistService.get(playlistId)
        if(_playlist == None):
            return 0

        _datetimeStarted = datetime.now()
        _newStreams = []
        for _sourceId in _playlist.streamSourceIds:
            _source = self.streamSourceService.get(_sourceId)
            _fetchedStreams = []
            
            if(_source == None):
                printS("StreamSource with ID ", _sourceId, " could not be found. Consider removing it using the purge commands.", color = BashColor.FAIL)
                continue
            
            if(not _source.enableFetch):
                continue

            if(_source.isWeb):
                if(_source.streamSourceTypeId == StreamSourceType.YOUTUBE.value):
                    _fetchedStreams = self.fetchYoutube(_source, batchSize, takeAfter, takeBefore)
                else:
                    # TODO handle other sources
                    continue
            else:
                # TODO handle directory sources
                continue

            if(len(_fetchedStreams) > 0):
                _source.lastSuccessfulFetched = _datetimeStarted
            
            _source.lastFetchedId = _fetchedStreams[1]
            _source.lastFetched = _datetimeStarted
            _updateSuccess = self.streamSourceService.update(_source)
            if(_updateSuccess):
                _newStreams += _fetchedStreams[0]
            else:
                printS("Could not update source \"", _source.name, "\" (ID: ", _source.id, "), streams could not be added: \n", _fetchedStreams, color = BashColor.WARNING)
                
            sys.stdout.flush()

        _updateResult = self.playlistService.addStreams(_playlist.id, _newStreams)
        if(len(_updateResult) > 0):
            return len(_newStreams)
        else:
            return 0

    def fetchYoutube(self, streamSource: StreamSource, batchSize: int = 10, takeAfter: datetime = None, takeBefore: datetime = None) -> tuple[List[QueueStream], str]:
        """
        Fetch videos from YouTube

        Args:
            batchSize (int): number of videos to check at a time, unrelated to max videos that will be read
            takeAfter (datetime): limit to take video after
            takeBefore (datetime): limit to take video before

        Returns:
            tuple[List[QueueStream], str]: A tuple of List of QueueStream, and the last YouTube ID fetched 
        """

        _channel = Channel(streamSource.uri)

        if(_channel == None or _channel.channel_name == None):
            printS("Channel \"", streamSource.name, "\" (URL: ", streamSource.uri, ") could not be found or is not valid. Please remove it and add it back.", color = BashColor.FAIL)
            return []

        printS("Fetching videos from ", _channel.channel_name, "...")
        if(len(_channel.video_urls) < 1):
            printS("Channel \"", _channel.channel_name, "\" has no videos.", color = BashColor.WARNING)
            return []

        _newStreams = []
        _videos = list(_channel.videos)
        _lastVideoId = _videos[0].video_id
        if(streamSource.lastFetchedId != None and _lastVideoId == streamSource.lastFetchedId):
            printS("DEBUG: fetchYoutube - last video fetched: \"", sanitize(_videos[0].title), "\", YouTube ID \"", _lastVideoId, "\"", color = BashColor.WARNING)
            printS("DEBUG: fetchYoutube - return due to _lastVideoId == streamSource.lastFetchedId", color = BashColor.WARNING)
            return (_newStreams, _lastVideoId)
            
        for i, yt in enumerate(_videos):
            if(takeAfter != None and yt.publish_date < takeAfter):
                printS("DEBUG: fetchYoutube - break due to takeAfter != None and yt.publish_date < takeAfter", color = BashColor.WARNING)
                break
            elif(takeBefore != None and yt.publish_date > takeBefore):
                printS("DEBUG: fetchYoutube - continue due to takeBefore != None and yt.publish_date > takeBefore", color = BashColor.WARNING)
                continue
            # Todo fetch batches using batchSize of videos instead of all 3000 videos in some cases taking 60 seconds+ to load
            elif(i > batchSize):
                printS("DEBUG: fetchYoutube - break due to i > batchSize", color = BashColor.WARNING)
                break
            
            _sanitizedTitle = sanitize(yt.title)
            printS("\tAdding a QueueStream with name \"", _sanitizedTitle, "\"...")
            _stream = QueueStream(name = _sanitizedTitle, 
                                           uri = yt.watch_url, 
                                           isWeb = True,
                                           streamSourceId = streamSource.id,
                                           watched = None,
                                           backgroundContent = streamSource.backgroundContent,
                                           added = datetime.now())
            _newStreams.append(_stream)
            
        return (_newStreams, _lastVideoId)
    
    def resetPlaylistFetch(self, playlistIds: List[str]) -> int:
        """
        Reset the fetch-status for sources of a playlist and deletes all streams.

        Args:
            playlistIds (List[str]): list of playlistIds 
            
        Returns:
            int: number of playlists reset
        """
        
        _result = 0
        for playlistId in playlistIds:            
            _playlist = self.playlistService.get(playlistId)
            _deleteUpdateResult = True
            
            for queueStreamId in _playlist.streamIds:
                _deleteStreamResult = self.queueStreamService.delete(queueStreamId)
                _deleteUpdateResult = _deleteUpdateResult and _deleteStreamResult != None
            
            _playlist.streamIds = []
            _updateplaylistResult = self.playlistService.update(_playlist)
            _deleteUpdateResult = _deleteUpdateResult and _updateplaylistResult != None
            
            for streamSourceId in _playlist.streamSourceIds:
                _streamSource = self.streamSourceService.get(streamSourceId)
                _streamSource.lastFetched = None
                _updateStreamResult = self.streamSourceService.update(_streamSource)
                _deleteUpdateResult = _deleteUpdateResult and _updateStreamResult != None
            
            if(_deleteUpdateResult):
                _result += 1
                
        return _result
