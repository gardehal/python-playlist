import os
from typing import List

from dotenv import load_dotenv
import mechanize
from pytube import YouTube
from myutil.Util import *

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
        self.quitArguments = ["-quit", "-q", "-exit", "-end"]
        self.skipArguments = ["-skip", "-s"]
        self.addCurrentToPlaylistArguments = ["-addto", "-at"]
        self.printPlaybackDetailsArguments = ["-detailsprint", "-details", "-print", "-dp"]
        self.printPlaybackHelpArguments = ["-help", "-h"]

        # Stream
        self.addStreamCommands = ["add", "a"]
        self.deleteStreamCommands = ["delete", "dm", "d"]
        self.restoreStreamCommands = ["restore", "r"]
        # Sources
        self.addSourcesCommands = ["addsource", "as"]
        self.deleteSourceCommands = ["deletesource", "ds"]
        self.restoreSourceCommands = ["restoresource", "rs"]
        self.listSourcesCommands = ["listsources", "ls"]
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
            printS("DEBUG: getPageTitle - Getting title from pytube.", color = colors["WARNING"], doPrint = DEBUG)
            _yt = YouTube(url)
            _title = _yt.title
        else:
            printS("DEBUG: getPageTitle - Getting title from mechanize.", color = colors["WARNING"], doPrint = DEBUG)
            _br = mechanize.Browser()
            _br.open(url)
            _title = _br.title()
            _br.close()

        return sanitize(_title).strip()
    
    def getIdsFromInput(self, input: List[str], existingIds: List[str], indexList: List[any], limit: int = None, returnOnNonIds: bool = False) -> List[str]:
        """
        Get IDs from a list of inputs, whether they are raw IDs that must be checked via the database or indices (formatted "i[index]") of a list.

        Args:
            input (List[str]): input if IDs/indices
            existingIds (List[str]): existing IDs to compare with
            indexList (List[any]): List of object (must have field "id") to index from
            limit (int): limit the numbers of arguments to parse
            returnOnNonIds (bool): return valid input IDs if the current input is no an ID, to allow input from user to be something like \"id id id bool\" which allows unspecified IDs before other arguments 

        Returns:
            List[str]: List of existing IDs for input which can be found
        """
        
        if(len(existingIds) == 0 or len(indexList) == 0):
            printS("DEBUG: getIdsFromInput - Length of input \"existingIds\" (", len(existingIds), ") or \"indexList\" (", len(indexList), ") was 0.", color = colors["WARNING"], doPrint = DEBUG)
            return []

        _result = []
        for i, _string in enumerate(input):
            if(limit != None and i >= limit):
                printS("DEBUG: getIdsFromInput - Returning data before input ", _string, ", limit (", limit, ") reached.", color = colors["WARNING"], doPrint = DEBUG)
                break
            
            if(_string[0] == "i"):  # Starts with "i", like index of "i2" is 2, "i123" is 123 etc.
                if(not isNumber(_string[1:])):
                    if(returnOnNonIds):
                        return _result
                    
                    printS("Argument ", _string, " is not a valid index format, must be \"i\" followed by an integer, like \"i0\". Argument not processed.", color = colors["FAIL"])
                    continue

                _index = int(float(_string[1:]))
                _indexedEntity = indexList[_index]

                if(_indexedEntity != None):
                    _result.append(_indexedEntity.id)
                else:
                    if(returnOnNonIds):
                        return _result
                    
                    printS("Failed to get data for index ", _index, ", it is out of bounds.", color = colors["FAIL"])
            else:  # Assume input is ID if it's not, users problem. Could also check if ID in getAllIds()
                if(_string in existingIds):
                    _result.append(_string)
                else:
                    if(returnOnNonIds):
                        return _result
                    
                    printS("Failed to add playlist with ID \"", _string, "\", no such entity found in database.", color = colors["FAIL"])
                    continue

        return _result
    
    def printLists(self, data: List[List[str]], titles: List[str]) -> bool:
        """
        Prints all lists in data, with title before corresponding list.

        Args:
            data (List[List[str]]): List if Lists to print
            titles (List[str]): List of titles, index 0 is title for data List index 0 etc.

        Returns:
            bool: true = success
        """
        
        for i, dataList in enumerate(data):
            printS("\n", titles[i], color = colors["BOLD"])
            printS("No data.", color = colors["WARNING"], doPrint = len(dataList) == 0) 
            
            for j, entry in enumerate(dataList):
                _color = "WHITE" if j % 2 == 0 else "GREYBG"
                printS(entry, color = colors[_color]) 
                
        return True
    
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
        _result += "\n" + str(self.detailsPlaylistCommands) + " [playlistIds or indices: list] [? enableFetch: bool] [? enableFetch: bool]: Prints details about given playlist, with option for including StreamSources and QueueStreams."
        _result += "\n" + str(self.fetchPlaylistSourcesCommands) + " [playlistIds or indices: list] [? takeAfter: datetime] [? takeBefore: datetime]: Fetch new streams from StreamSources in Playlists indicated, e.g. if a Playlist has a YouTube channel as a source, and the channel uploads a new video, this video will be added to the Playlist. Optional arguments takeAfter: only fetch QueueStreams after this date, takeBefore: only fetch QueueStreams before this date. Dates formatted like \"2022-01-30\" (YYYY-MM-DD)."
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