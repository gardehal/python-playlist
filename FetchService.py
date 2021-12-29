from myutil.DateTimeObject import DateTimeObject
from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService
from enums.StreamSourceType import StreamSourceType
from model.Playlist import *
from myutil.Util import *
from model.QueueStream import QueueStream
from pytube import Channel
from model.StreamSourceCollection import StreamSourceCollection
from dotenv import load_dotenv

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

class FetchService():
    debug: bool = DEBUG
    storagePath: str = LOCAL_STORAGE_PATH
    playlistService: PlaylistService = None

    def __init__(self):
        self.playlistService: str = PlaylistService()
        self.queueStreamService: str = QueueStreamService()

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
        
        _playlist = self.get(playlistId)
        if(_playlist == None):
            return 0

        _sourceCollection = self.videoSourceCollectionRepository.get(_playlist.sourceCollectionId)
        if(_sourceCollection == None):
            return 0

        _lastFetch = _sourceCollection.lastFetched
        _newVideos = []
        for _source in _sourceCollection.videoSourceIds:
            if(not _source.enableFetch):
                continue

            if(_source.isWeb):
                if(_source.videoSourceTypeId == StreamSourceType.YOUTUBE.value):
                    _newVideos += self.fetchYoutube(_source, batchSize, _lastFetch, takeBefore)
                else:
                    # TODO handle other sources
                    continue
            else:
                # TODO handle directory sources
                continue
        
        for _video in _newVideos:
            self.queueStreamService.add(_video)
            _playlist.streamIds.append(_video.id)
            
        _playlist.lastUpdated = datetime.now()
        _updateSuccess = self.update(_playlist)
        if(_updateSuccess):
            return len(_newVideos)
        else:
            return 0
               
    def fetchYoutube(self, videoSource: StreamSourceCollection, batchSize: int, takeAfter: datetime, takeBefore: datetime) -> List[QueueStream]:
        """
        Fetch videos from YouTube

        Args:
            batchSize (int): number of videos to check at a time, unrelated to max videos that will be read
            takeAfter (datetime): limit to take video after
            takeBefore (datetime): limit to take video before

        Returns:
            List[QueueStream]: List of QueueStream
        """
        
        if(self.debug): printS("fetchYoutube start, fetching channel source")
        _channel = Channel(videoSource.url)
        
        if(_channel == None or _channel.channel_name == None):
            printS("Channel ", videoSource.name, " ( ", videoSource.url, " ) could not be found or is not valid. Please remove it and add it back.", color=colors["ERROR"])
            return []
        
        if(self.debug): printS("Fetching videos from ", _channel.channel_name)
        if(len(_channel.video_urls) < 1):
            printS("Channel ", _channel.channel_name, " has no videos.", color=colors["WARNING"])
            return []
        
        _newVideos = []
        for i, yt in enumerate(_channel.videos):
            publishedDto = DateTimeObject().fromDatetime(yt.publish_date)
                      
            if(takeAfter != None and publishedDto.now < takeAfter):
                break
            if(takeBefore != None and publishedDto.now > takeBefore):
                continue
            
            _newVideos.append(QueueStream(yt.title, yt.watch_url, True, None, datetime.now(), videoSource.id))
            
            # Todo fetch batches using batchSize of videos instead of all 3000 videos in some cases taking 60 seconds+ to load
            if(i > 10):
                printS("WIP: Cannot get all videos. Taking last ", len(_newVideos))
                break
        
        return _newVideos