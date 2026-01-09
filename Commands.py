from grdUtil.StaticUtil import StaticUtil
from Argumentor import *

from enums.CommandHitValues import CommandHitValues

class Commands():
    
    def __init__(self):
        # General
        helpCommand = Command("Help", ["help", "h", "man"], CommandHitValues.HELP,
            description= "Print this documentation.")
        testCommand = Command("Test", ["test", "t"], CommandHitValues.TEST,
            description= "A method of calling experimental code (when you want to test if something works).")
        editCommand = Command("Edit", ["edit", "e"], CommandHitValues.EDIT,
            description= "")
        searchCommand = Command("Search", ["search", "s"], CommandHitValues.SEARCH,
            description= "")
        listSettingsCommand = Command("ListSettings", ["settings", "secrets"], CommandHitValues.LIST_SETTINGS,
            description= "Lists settings currently used by program. These settings can also be found in the file named \".env\" with examples in the file \".env-example\".")
        
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
        self.detailsPlaylistCommands = ["detailsplaylist", "dp"]
        self.ListWatchedCommands = ["listwatched", "lw"]
        self.fetchPlaylistSourcesCommands = ["fetch", "f", "update", "u"]
        self.prunePlaylistCommands = ["prune"]
        self.purgePlaylistCommands = ["purgeplaylists", "pp"]
        self.purgeCommands = ["purge"]
        self.resetPlaylistFetchCommands = ["reset"]
        self.downloadPlaylistCommands = ["downloadplaylist", "dwpl"]
        self.exportPlaylistCommands = ["export"]
        self.unwatchAllPlaylistCommands = ["unwatchall"]
        
        # Playback
        self.playCommands = ["play", "p"]
        self.quitArguments = StaticUtil.quit
        self.quitWatchedArguments = ["quitwatched", "qw", "wq"]
        self.skipArguments = ["skip", "s", "[C"] # [C = right arrow
        self.repeatArguments = ["repeat", "r"]
        self.listPlaylistArguments = ["listplaylists", "lp"]
        self.addCurrentToPlaylistArguments = ["addto", "at"]
        self.circumventRestricted = ["circumventrestricted", "circumvent", "restricted", "cr"]
        self.printPlaybackDetailsArguments = ["detailsprint", "details", "print", "dp"]
        self.nextArguments = ["next", "n"]
        self.printPlaybackHelpArguments = ["help", "h"]

        # Stream
        self.addStreamCommands = ["add", "a"]
        self.addMultipleStreamsCommands = ["addmultiple", "am"]
        self.deleteStreamCommands = ["delete", "dm", "d"]
        self.restoreStreamCommands = ["restore", "r"]
        # Sources
        self.addSourcesCommands = ["addsource", "as"]
        self.deleteSourceCommands = ["deletesource", "ds"]
        self.restoreSourceCommands = ["restoresource", "rs"]
        self.listSourcesCommands = ["listsources", "ls"]
        self.openSourceCommands = ["opensource", "os"]
        # Meta
        self.listSettingsCommands = ["settings", "secrets"]
        self.listSoftDeletedCommands = ["listsoftdeleted", "listdeleted", "lsd", "ld"]
        self.refactorCommands = ["refactor"]
        
    def getHelpString(self) -> str:
        """
        Get all help-info.

        Returns:
            str: a string of all help-info
        """

        result = ""
        result += self.getGeneralHelpString()
        result += "\n"
        result += self.getPlaylistHelpString()
        result += "\n"
        result += self.getQueueStreamHelpString()
        result += "\n"
        result += self.getStreamSourceHelpString()
        result += "\n"
        result += self.getMetaHelpString()
        
        return result
        
    def getGeneralHelpString(self) -> str:
        """
        Get the general overhead help-print as a string.

        Returns:
            str: a string of general overhead info
        """

        result = ""
        result += "\n--- Help ---"
        result += "\nArguments marked with ? are optional."
        result += "\nAll arguments must be separated by space only."
        result += "\nWhen using an index or indices, format with with an \"i\" followed by the index, like \"i1\"."
        result += "\nExample, print the detail so if first Playlist: \"main.py dp i1\""
        result += "\n\n"

        result += "\n" + str(self.helpCommands) + ": Prints this information about input arguments."
        result += "\n" + str(self.testCommands) + ": A method of calling experimental code (when you want to test if something works)."
        result += "\n" + str(self.editCommands) + " [playlistId or index: str]: Opens the file with Playlist."
        result += "\n" + str(self.searchCommands) + " [searchTerm: str] [? includeSoftDeleted: bool]: Search all Playlists, QueueStreams, and StreamQueues, uri and names where available. Supports Regex."

        return result
    
    def getPlaylistHelpString(self) -> str:
        """
        Get the Playlist-section of help-print as a string.

        Returns:
            str: a string of Playlist info
        """

        result = ""
        result += "\n" + str(self.addPlaylistCommands) + " [name: str] [? playWatchedStreams: bool] [? allowDuplicates: bool] [? streamSourceIds: list]: Add a Playlist with name: name, playWatchedStreams: if playback should play watched QueueStreams, allowDuplicates: should Playlist allow duplicate QueueStreams (only if the uri is the same), streamSourceIds: a list of StreamSources."
        result += "\n" + str(self.addPlaylistFromYouTubeCommands) + " [youTubePlaylistUrl: str] [? name: str] [? playWatchedStreams: bool] [? allowDuplicates: bool]: Add a Playlist and populate it with QueueStreams from given YouTube playlist youTubePlaylistUrl, with name: name, playWatchedStreams: if playback should play watched streams, allowDuplicates: should Playlist allow duplicate QueueStreams (only if the uri is the same)."
        result += "\n" + str(self.deletePlaylistCommands) + " [playlistIds or indices: list]: deletes Playlists indicated."
        result += "\n" + str(self.restoreSourceCommands) + " [playlistIds or index: str]: restore soft deleted Playlist from database."
        result += "\n" + str(self.listPlaylistCommands) + " [? includeSoftDeleted: bool]: List Playlists with indices that can be used instead of IDs in other commands."
        result += "\n" + str(self.detailsPlaylistCommands) + " [playlistIds or indices: list] [? includeUri: bool] [? includeId: bool] [? includeDaterTime: bool] [? includeListCount: bool] [? includeSource: bool]: Prints details about given playlist, with option for including fields of StreamSources and QueueStreams (like datetimes or IDs)."
        result += "\n" + str(self.fetchPlaylistSourcesCommands) + " [playlistIds or indices: list] [? takeAfter: datetime] [? takeBefore: datetime] [? takeNewOnly: bool]: Fetch new streams from StreamSources in Playlists indicated, e.g. if a Playlist has a YouTube channel as a source, and the channel uploads a new video, this video will be added to the Playlist. Optional arguments takeAfter: only fetch QueueStreams after this date, takeBefore: only fetch QueueStreams before this date. Dates formatted like \"2022-01-30\" (YYYY-MM-DD)."
        result += "\n" + str(self.prunePlaylistCommands) + " [playlistIds or indices: list] [? includeSoftDeleted: bool] [? permanentlyDelete: bool]: Prune Playlists indicated, deleting watched QueueStreams."
        result += "\n" + str(self.purgePlaylistCommands) + ": Purge all Playlists, removing IDs with no corresponding relation and deleting StreamSources and QueueStreams with no linked IDs in Playlists."
        result += "\n" + str(self.purgeCommands) + ": Purge all soft deleted entities."
        result += "\n" + str(self.resetPlaylistFetchCommands) + " [playlistIds or indices: list]: Resets fetch status of StreamSources in a Playlist and deletes QueueStreams from Playlist."
        result += "\n" + str(self.playCommands) + " [playlistId or index: str] [? startIndex: int] [? shuffle: bool] [? repeat: bool]: Start playing stream from a Playlist, order and automation (like skipping already watched QueueStreams) depending on the input and Playlist."
        result += "\n" + str(self.downloadPlaylistCommands) + " [playlistId or index: str] [? directoryName: str] [? startIndex: int] [? endIndex: int] [? streamNameRegex: str] [? useIndex: bool]: Download streams from web sources for given playlist, with optional directory name (under localStoragePath in settings), start-end index, regex for naming streams (e.g. all streams are named \"Podcast guys: Actual Title\", use regex \": (.*)\", including \"s), and option to add index (+1) on stream names so they naturally sort in order."
        result += "\n" + str(self.exportPlaylistCommands) + " [playlistId or index: str] [? directoryName: str]: Export all sources and streams in a list to a text files."
        # result += "\n" + str(self.unwatchAllPlaylistCommands) + " [playlistId or index: str]: Mark all streams in a playlist as unwatched."
        result += self.getPlaylistArgumentsHelpString()
        
        return result
    
    def getPlaylistArgumentsHelpString(self) -> str:
        """
        Get the Playlist-section Arguments of help-print as a string.

        Returns:
            str: a string of Playlist Arguments info
        """

        result = ""
        result += "\n\t" + str(list(set(self.quitArguments))) + ": End current playback and continue the program without playing anymore QueueStreams in Playlist. Only available while Playlist is playing."
        result += "\n\t" + str(self.quitWatchedArguments) + ": Mark current stream as watched and end playback as with quit. Only available while Playlist is playing."
        result += "\n\t" + str(self.skipArguments) + " [nSkip: int]: Skip current QueueStream playing. This QueueStream will not be marked as watched. Only available while Playlist is playing. Optional argument to skip multiple by giving number to skip, default 1 (current stream only)."
        result += "\n\t" + str(self.repeatArguments) + ": Repeat current QueueStream."
        result += "\n\t" + str(self.listPlaylistArguments) + ": List Playlists."
        result += "\n\t" + str(self.addCurrentToPlaylistArguments) + " [playlistId or index: str]: Add the current QueueStream to another Playlist indicated by ID on index. Only available while Playlist is playing."
        result += "\n\t" + str(self.circumventRestricted) + ": Open a website that will get around age-restricted video in case you are not logged in. Only use if you are 18 or older!"
        result += "\n\t" + str(self.printPlaybackDetailsArguments) + ": Prints details of current playing Playlist."
        result += "\n\t" + str(self.nextArguments) + ": Prints simple list of next streams."
        result += "\n\t" + str(self.printPlaybackHelpArguments) + ": Prints relevant help during playback."
        
        return result
        
    def getQueueStreamHelpString(self) -> str:
        """
        Get the QueueStream-section help-print as a string.

        Returns:
            str: a string of QueueStream info
        """

        result = ""
        result += "\n" + str(self.addStreamCommands) + " [playlistId or index: str] [uri: str] [? name: str]: Add a stream to a Playlist from ID or index, from uri: URL, and name: name (set automatically if not given)."
        result += "\n" + str(self.addMultipleStreamsCommands) + " [playlistId or index: str] [uris: str]: Add multiple streams to a Playlist from ID or index, from uris (set automatically)."
        result += "\n" + str(self.deleteStreamCommands) + " [playlistId or index: str] [streamIds or indices: list]: Delete QueueStreams from Playlist."
        result += "\n" + str(self.restoreStreamCommands) + " [playlistId or index: str] [streamIds or indices: str]: Restore soft deleted QueueStreams from database."

        return result
    
    def getStreamSourceHelpString(self) -> str:
        """
        Get the StreamSource-section help-print as a string.

        Returns:
            str: a string of StreamSource info
        """

        result = ""
        result += "\n" + str(self.addSourcesCommands) + " [playlistId or index: str] [uri: string] [? enableFetch: bool] [? backgroundContent: bool] [? name: str]: Add a StreamSources from uri: URL, enableFetch: if the Playlist should fetch new QueueStream from this StreamSource, backgroundContent; if the QueueStream from this source are things you would play in the background, and name: name (set automatically if not given)."
        result += "\n" + str(self.deleteSourceCommands) + " [playlistId or index: str] [sourceIds or indices: str]: Delete StreamSources from database."
        result += "\n" + str(self.restoreSourceCommands) + " [playlistId or index: str] [sourceIds or indices: str]: Restore soft deleted StreamSources from database."
        result += "\n" + str(self.listSourcesCommands) + " [? includeSoftDeleted: bool]: Lists StreamSources with indices that can be used instead of IDs in other commands."
        result += "\n" + str(self.openSourceCommands) + "[sourceIds or indices: str]: open StreamSources in web if it is a web source, or directory if not."

        return result
    
    def getMetaHelpString(self) -> str:
        """
        Get the meta-section help-print as a string.

        Returns:
            str: a string of meta info
        """

        result = ""
        result += "\n" + str(self.listSettingsCommands) + ": Lists settings currently used by program. These settings can also be found in the file named \".env\" with examples in the file \".env-example\"."
        result += "\n" + str(self.listSoftDeletedCommands) + " [? simplified: bool]: Lists all soft deleted entities. Option for simplified, less verbose list."
        result += "\n" + str(self.refactorCommands) + ": Refactor old code/data (JSON-file storage only)."

        return result
    