from myutil.DateTimeObject import DateTimeObject
from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService
from StreamSourceService import StreamSourceService
from enums.StreamSourceType import StreamSourceType
from model.Playlist import *
from myutil.Util import *
from model.QueueStream import *
from pytube import Channel
from dotenv import load_dotenv

from model.StreamSource import StreamSource

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

class FetchService():
    debug: bool = DEBUG
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

        _newStreams = []
        for _sourceId in _playlist.streamSourceIds:
            _source = self.streamSourceService.get(_sourceId)
            if(_source == None):
                if(self.debug): printS("StreamSource with ID ", _sourceId, " could not be found. Consider removing it using the purge commands.", color=colors["WARNING"])
                continue

            if(not _source.enableFetch):
                continue

            _fetchedStreams = None
            if(_source.isWeb):
                if(_source.videoSourceTypeId == StreamSourceType.YOUTUBE.value):
                    _fetchedStreams = self.fetchYoutube(_source, batchSize, _source.lastFetched, takeBefore)
                else:
                    # TODO handle other sources
                    continue
            else:
                # TODO handle directory sources
                continue

            _source.lastFetched = datetime.now()
            _updateSuccess = self.streamSourceService.update(_source)
            if(_updateSuccess):
                _newStreams += _fetchedStreams
            else:
                printS("Could not update source \"", _source.name, "\" (ID: ", _source.id, "), streams could not be added: \n", _fetchedStreams, color=colors["WARNING"])
        
        for _stream in _newStreams:
            self.queueStreamService.add(_stream)
            
        self.playlistService.addStreamsToPlaylist(_playlist.id, _newStreams)

        _playlist.lastUpdated = datetime.now()
        _updateSuccess = self.playlistService.update(_playlist)
        if(_updateSuccess):
            return len(_newStreams)
        else:
            return 0
               
    def fetchYoutube(self, streamSource: StreamSource, batchSize: int, takeAfter: datetime, takeBefore: datetime) -> List[QueueStream]:
        """
        Fetch videos from YouTube

        Args:
            batchSize (int): number of videos to check at a time, unrelated to max videos that will be read
            takeAfter (datetime): limit to take video after
            takeBefore (datetime): limit to take video before

        Returns:
            List[QueueStream]: List of QueueStream
        """
        
        if(self.debug): printS("fetchYoutube start, fetching channel source...")
        _channel = Channel(streamSource.uri)
        
        if(_channel == None or _channel.channel_name == None):
            printS("Channel \"", streamSource.name, "\" (URL: ", streamSource.uri, ") could not be found or is not valid. Please remove it and add it back.", color=colors["ERROR"])
            return []
        
        if(self.debug): printS("Fetching videos from ", _channel.channel_name, "...")
        if(len(_channel.video_urls) < 1):
            printS("Channel \"", _channel.channel_name, "\" has no videos.", color=colors["WARNING"])
            return []
        
        _newStreams = []
        for i, yt in enumerate(_channel.videos):
            publishedDto = DateTimeObject().fromDatetime(yt.publish_date)
            takeAfterDto = DateTimeObject().fromString(takeAfter)
            takeBeforeDto = DateTimeObject().fromString(takeBefore)

            if(takeAfter != None and publishedDto.now < takeAfterDto.now):
                break
            if(takeBefore != None and publishedDto.now > takeBeforeDto.now):
                continue
            
            _newStreams.append(QueueStream(yt.title, yt.watch_url, True, None, datetime.now(), streamSource.id))
            
            # Todo fetch batches using batchSize of videos instead of all 3000 videos in some cases taking 60 seconds+ to load
            if(i > batchSize):
                printS("WIP: Cannot get all videos. Taking last ", len(_newStreams))
                break
        
        return _newStreams