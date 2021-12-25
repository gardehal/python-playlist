
class Settings():
    def __init__(self, 
                 storagePath: str = None, 
                 logWatched: bool = False,
                 downloadWebVideos: bool = False, 
                 removeWatchedOnFetch: bool = False):
        self.storagePath: str = storagePath
        self.logWatched: bool = logWatched
        self.downloadWebVideos: bool = downloadWebVideos
        self.removeWatchedOnFetch: bool = removeWatchedOnFetch