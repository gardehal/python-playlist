import os
from typing import List

import mechanize
from dotenv import load_dotenv
from myutil.BashColor import BashColor
from myutil.InputUtil import isNumber, sanitize
from myutil.PrintUtil import printS
from pytube import YouTube

from enums.StreamSourceType import StreamSourceType, StreamSourceTypeUtil

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")
LOG_WATCHED = eval(os.environ.get("LOG_WATCHED"))
DOWNLOAD_WEB_STREAMS = eval(os.environ.get("DOWNLOAD_WEB_STREAMS"))
REMOVE_WATCHED_ON_FETCH = eval(os.environ.get("REMOVE_WATCHED_ON_FETCH"))
PLAYED_ALWAYS_WATCHED = eval(os.environ.get("PLAYED_ALWAYS_WATCHED"))
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")
BROWSER_BIN = os.environ.get("BROWSER_BIN")

class Utility():
    
    def __init__(self):
        # General
        self.helpCommands = ["help", "h"]
        self.testCommands = ["test", "t"]
        self.editCommands = ["edit", "e"]
        self.searchCommands = ["search", "s"]

        # Playlist
        self.addPlaylistCommands = ["addplaylist", "apl", "ap"]
        self.addPlaylistFromYouTubeCommands = ["fromyoutube", "fyt", "fy"]
        self.deletePlaylistCommands = ["deleteplaylist", "dpl"]
        self.restorePlaylistCommands = ["restoreplaylist", "rpl", "rp"]
        self.listPlaylistCommands = ["listplaylist", "lpl", "lp"]
        self.detailsPlaylistCommands = ["detailsplaylist", "dpl", "dp"]
        self.fetchPlaylistSourcesCommands = ["fetch", "f", "update", "u"]
        self.prunePlaylistCommands = ["prune"]
        self.purgePlaylistCommands = ["purge"]
        self.resetPlaylistFetchCommands = ["reset"]
        self.playCommands = ["play", "p"]
        self.quitArguments = ["quit", "q", "exit", "end"]
        self.skipArguments = ["skip", "s"]
        self.repeatArguments = ["repeat", "r"]
        self.listPlaylistArguments = ["listplaylists", "lp"]
        self.addCurrentToPlaylistArguments = ["addto", "at"]
        self.printPlaybackDetailsArguments = ["detailsprint", "details", "print", "dp"]
        self.printPlaybackHelpArguments = ["help", "h"]

        # Stream
        self.addStreamCommands = ["add", "a"]
        self.deleteStreamCommands = ["delete", "dm", "d"]
        self.restoreStreamCommands = ["restore", "r"]
        # Sources
        self.addSourcesCommands = ["addsource", "as"]
        self.deleteSourceCommands = ["deletesource", "ds"]
        self.restoreSourceCommands = ["restoresource", "rs"]
        self.listSourcesCommands = ["listsources", "ls"]
        self.openCommands = ["opensource", "os"]
        # Meta
        self.listSettingsCommands = ["settings", "secrets"]
        self.listSoftDeletedCommands = ["listsoftdeleted", "listdeleted", "lsd", "ld"]

    def getPageTitle(self, url: str) -> str:
        """
        Get page title from the URL url, using mechanize or PyTube.

        Args:
            url (str): URL to page to get title from

        Returns:
            str: Title of page
        """

        _title = ""
        
        _isYouTubeChannel = "user" in url or "channel" in url  
        if(StreamSourceTypeUtil.strToStreamSourceType(url) == StreamSourceType.YOUTUBE and not _isYouTubeChannel):
            printS("DEBUG: getPageTitle - Getting title from pytube.", color = BashColor.WARNING, doPrint = DEBUG)
            _yt = YouTube(url)
            _title = _yt.title
        else:
            printS("DEBUG: getPageTitle - Getting title from mechanize.", color = BashColor.WARNING, doPrint = DEBUG)
            _br = mechanize.Browser()
            _br.open(url)
            _title = _br.title()
            _br.close()

        return sanitize(_title).strip()
    
    def getAllSettingsAsString(self) -> str:
        """
        Print settings in .env settings/secrets file.

        Returns:
            str: a string of all settings/secrets in project from .env.
        """

        printS("DEBUG: ", DEBUG,
               "\n", "LOCAL_STORAGE_PATH: ", LOCAL_STORAGE_PATH,
               "\n", "LOG_WATCHED: ", LOG_WATCHED,
               "\n", "DOWNLOAD_WEB_STREAMS: ", DOWNLOAD_WEB_STREAMS,
               "\n", "REMOVE_WATCHED_ON_FETCH: ", REMOVE_WATCHED_ON_FETCH,
               "\n", "PLAYED_ALWAYS_WATCHED: ", PLAYED_ALWAYS_WATCHED,
               "\n", "WATCHED_LOG_FILEPATH: ", WATCHED_LOG_FILEPATH,
               "\n", "BROWSER_BIN: ", BROWSER_BIN)
        
    def getHelpString(self) -> str:
        """
        Get all help-info.

        Returns:
            str: a string of all help-info
        """

        _result = ""
        _result += self.getGeneralHelpString()
        _result += "\n"
        _result += self.getPlaylistHelpString()
        _result += "\n"
        _result += self.getQueueStreamHelpString()
        _result += "\n"
        _result += self.getStreamSourceHelpString()
        _result += "\n"
        _result += self.getMetaHelpString()
        
        return _result
        
    def getGeneralHelpString(self) -> str:
        """
        Get the general overhead help-print as a string.

        Returns:
            str: a string of general overhead info
        """

        _result = ""
        _result += "\n--- Help ---"
        _result += "\nArguments marked with ? are optional."
        _result += "\nAll arguments that triggers a function start with dash(-)."
        _result += "\nAll arguments must be separated by space only."
        _result += "\nWhen using an index or indices, format with with an \"i\" followed by the index, like \"i0\"."
        _result += "\n\n"

        _result += "\n" + str(self.helpCommands) + ": Prints this information about input arguments."
        _result += "\n" + str(self.testCommands) + ": A method of calling experimental code (when you want to test if something works)."
        _result += "\n" + str(self.editCommands) + " [playlistId or index: str]: Opens the file with Playlist."
        _result += "\n" + str(self.searchCommands) + " [searchTerm: str] [? includeSoftDeleted: bool]: Search all Playlists, QueueStreams, and StreamQueues, uri and names where available. Supports Regex."

        return _result
    
    def getPlaylistHelpString(self) -> str:
        """
        Get the Playlist-section of help-print as a string.

        Returns:
            str: a string of Playlist info
        """

        _result = ""
        _result += "\n" + str(self.addPlaylistCommands) + " [name: str] [? playWatchedStreams: bool] [? allowDuplicates: bool] [? streamSourceIds: list]: Add a Playlist with name: name, playWatchedStreams: if playback should play watched QueueStreams, allowDuplicates: should Playlist allow duplicate QueueStreams (only if the uri is the same), streamSourceIds: a list of StreamSources."
        _result += "\n" + str(self.addPlaylistFromYouTubeCommands) + " [youTubePlaylistUrl: str] [? name: str] [? playWatchedStreams: bool] [? allowDuplicates: bool]: Add a Playlist and populate it with QueueStreams from given YouTube playlist youTubePlaylistUrl, with name: name, playWatchedStreams: if playback should play watched streams, allowDuplicates: should Playlist allow duplicate QueueStreams (only if the uri is the same)."
        _result += "\n" + str(self.deletePlaylistCommands) + " [playlistIds or indices: list]: deletes Playlists indicated."
        _result += "\n" + str(self.restoreSourceCommands) + " [playlistIds or index: str]: restore soft deleted Playlist from database."
        _result += "\n" + str(self.listPlaylistCommands) + " [? includeSoftDeleted: bool]: List Playlists with indices that can be used instead of IDs in other commands."
        _result += "\n" + str(self.detailsPlaylistCommands) + " [playlistIds or indices: list] [? includeUri: bool] [? includeId: bool] [? includeDatertime: bool] [? includeListCount: bool] [? includeSource: bool]: Prints details about given playlist, with option for including fields of StreamSources and QueueStreams (like datetimes or IDs)."
        _result += "\n" + str(self.fetchPlaylistSourcesCommands) + " [playlistIds or indices: list] [? takeAfter: datetime] [? takeBefore: datetime] [? takeNewOnly: bool]: Fetch new streams from StreamSources in Playlists indicated, e.g. if a Playlist has a YouTube channel as a source, and the channel uploads a new video, this video will be added to the Playlist. Optional arguments takeAfter: only fetch QueueStreams after this date, takeBefore: only fetch QueueStreams before this date. Dates formatted like \"2022-01-30\" (YYYY-MM-DD)."
        _result += "\n" + str(self.prunePlaylistCommands) + " [playlistIds or indices: list]: Prune Playlists indicated, deleteing watched QueueStreams."
        _result += "\n" + str(self.purgePlaylistCommands) + " [? includeSoftDeleted: bool] [? permanentlyDelete: bool]: Purge database indicated, removing IDs with no corresponding relation and deleteing StreamSources and QueueStreams with no linked IDs in Playlists."
        _result += "\n" + str(self.resetPlaylistFetchCommands) + " [playlistIds or indices: list]: Resets fetch status of StreamSources in a Playlist and deletes QueueStreams from Playlist."
        _result += "\n" + str(self.playCommands) + " [playlistId or index: str] [? starindex: int] [? shuffle: bool] [? repeat: bool]: Start playing stream from a Playlist, order and automation (like skipping already watched QueueStreams) depending on the input and Playlist."
        _result += self.getPlaylistArgumentsHelpString()
        
        return _result
    
    def getPlaylistArgumentsHelpString(self) -> str:
        """
        Get the Playlist-section Arguments of help-print as a string.

        Returns:
            str: a string of Playlist Arguments info
        """

        _result = ""
        _result += "\n\t" + str(self.quitArguments) + ": End current playback and contintue the program without playing anymore QueueStreams in Playlist. Only available while Playlist is playing."
        _result += "\n\t" + str(self.skipArguments) + ": Skip current QueueStream playing. This QueueStream will not be marked as watched. Only available while Playlist is playing."
        _result += "\n\t" + str(self.repeatArguments) + ": Repeat current QueueStream."
        _result += "\n\t" + str(self.listPlaylistArguments) + ": List Playlists."
        _result += "\n\t" + str(self.addCurrentToPlaylistArguments) + " [playlistId or index: str]: Add the current QueueStream to another Playlist indicated by ID on index. Only available while Playlist is playing."
        _result += "\n\t" + str(self.printPlaybackDetailsArguments) + ": Prints details of current playing Playlist."
        _result += "\n\t" + str(self.printPlaybackHelpArguments) + ": Prints relevant help during playback."
        
        return _result
        
    def getQueueStreamHelpString(self) -> str:
        """
        Get the QueueStream-section help-print as a string.

        Returns:
            str: a string of QueueStream info
        """

        _result = ""
        _result += "\n" + str(self.addStreamCommands) + " [playlistId or index: str] [uri: string] [? name: str]: Add a stream to a Playlist from ID or index, from uri: URL, and name: name (set automatically if not given)."
        _result += "\n" + str(self.deleteStreamCommands) + " [playlistId or index: str] [streamIds or indices: list]: delete QueueStreams from Playlist."
        _result += "\n" + str(self.restoreStreamCommands) + " [playlistId or index: str] [streamIds or indices: str]: restore soft deleted QueueStreams from database."

        return _result
    
    def getStreamSourceHelpString(self) -> str:
        """
        Get the StreamSource-section help-print as a string.

        Returns:
            str: a string of StreamSource info
        """

        _result = ""
        _result += "\n" + str(self.addSourcesCommands) + " [playlistId or index: str] [uri: string] [? enableFetch: bool] [? name: str]: Add a StreamSources from uri: URL, enableFetch: if the Playlist should fetch new stream from this StreamSource, and name: name (set automatically if not given)."
        # _result += "\n" + str(self.addSourcesCommands) + " [playlistId or index: str] [uri: string] [? enableFetch: bool] [? backgroundContent: bool] [? name: str]: Add a StreamSources from uri: URL, enableFetch: if the Playlist should fetch new QueueStream from this StreamSource, backgroundContent; if the QueueStream from this source are things you would play in the background, and name: name (set automatically if not given)."
        _result += "\n" + str(self.deleteSourceCommands) + " [playlistId or index: str] [sourceIds or indices: str]: deletes StreamSources from database and Playlist if used anywhere."
        _result += "\n" + str(self.restoreSourceCommands) + " [playlistId or index: str] [sourceIds or indices: str]: restore soft deleted StreamSources from database."
        _result += "\n" + str(self.listSourcesCommands) + " [? includeSoftDeleted: bool]: Lists StreamSources with indices that can be used instead of IDs in other commands."
        _result += "\n" + str(self.openCommands) + ": Open StreamSources in web if it is a web source, or directory if not."

        return _result
    
    def getMetaHelpString(self) -> str:
        """
        Get the meta-section help-print as a string.

        Returns:
            str: a string of meta info
        """

        _result = ""
        _result += "\n" + str(self.listSettingsCommands) + ": Lists settings currently used by program. These settings can also be found in the file named \".env\" with examples in the file \".env-example\"."
        _result += "\n" + str(self.listSoftDeletedCommands) + " [? simplified: bool]: Lists all soft deleted entities. Option for simplified, less verbose list."

        return _result
    