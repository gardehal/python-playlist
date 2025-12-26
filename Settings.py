import os
import shutil

from dotenv import load_dotenv
from grdUtil.PrintUtil import asTable, printS

load_dotenv()

class Settings():
    debug: bool = None
    localStoragePath: str = None
    logWatched: str = None
    downloadWebStreams: bool = None
    removeWatchedOnFetch: bool = None
    playedAlwaysWatched: bool = None
    watchedLogFilepath: str = None
    logDirPath: str = None
    browserName: str = None
    fetchLimitSingleSource: int = None
    
    def __init__(self):
        envFilePath = ".env"
        envFilePathExample = ".env-example"
        if(not os.path.exists(envFilePath) and os.path.exists(envFilePathExample)):
            shutil.copy2(envFilePathExample, envFilePath)
            printS("Created a setting file, ", envFilePath, ", you may want to update some of the settings for security purposes according to the installation guide in README.md.\n\n", color = BashColor.OKGREEN)

        self.debug = eval(os.environ.get("DEBUG"))
        self.localStoragePath = os.environ.get("LOCAL_STORAGE_PATH")
        self.logWatched = eval(os.environ.get("LOG_WATCHED"))
        self.downloadWebStreams = eval(os.environ.get("DOWNLOAD_WEB_STREAMS"))
        self.removeWatchedOnFetch = eval(os.environ.get("REMOVE_WATCHED_ON_FETCH"))
        self.playedAlwaysWatched = eval(os.environ.get("PLAYED_ALWAYS_WATCHED"))
        self.watchedLogFilepath = os.environ.get("WATCHED_LOG_FILEPATH")
        self.logDirPath = os.environ.get("LOG_DIR_PATH")
        self.browserName = os.environ.get("BROWSE_NAME")
        self.fetchLimitSingleSource =  int(os.environ.get("FETCH_LIMIT_SINGLE_SOURCE"))
    
    def getAllSettingsAsString(self) -> str:
        """
        Get settings in .env settings/secrets file.

        Returns:
            str: a string of all settings/secrets in project from .env.
        """

        return joinAsString("DEBUG: ", self.debug,
               "\n", "LOCAL_STORAGE_PATH: ", self.localStoragePath,
               "\n", "LOG_WATCHED: ", self.logWatched,
               "\n", "DOWNLOAD_WEB_STREAMS: ", self.downloadWebStreams,
               "\n", "REMOVE_WATCHED_ON_FETCH: ", self.removeWatchedOnFetch,
               "\n", "PLAYED_ALWAYS_WATCHED: ", self.playedAlwaysWatched,
               "\n", "WATCHED_LOG_FILEPATH: ", self.watchedLogFilepath,
               "\n", "LOG_DIR_PATH: ", self.logDirPath,
               "\n", "BROWSE_NAME: ", self.browserName,
               "\n", "FETCH_LIMIT_SINGLE_SOURCE: ", self.fetchLimitSingleSource)
        
    def getAllSettingsAsTable(self) -> str:
        """
        Get settings in .env settings/secrets file as a table.

        Returns:
            str: a string of all settings/secrets in project from .env as a table.
        """

        names = ["DEBUG",
            "LOCAL_STORAGE_PATH", 
            "LOG_WATCHED", 
            "DOWNLOAD_WEB_STREAMS", 
            "REMOVE_WATCHED_ON_FETCH", 
            "PLAYED_ALWAYS_WATCHED", 
            "WATCHED_LOG_FILEPATH", 
            "LOG_DIR_PATH", 
            "BROWSE_NAME", 
            "FETCH_LIMIT_SINGLE_SOURCE"]
        settings = [self.debug,
            self.localStoragePath,
            self.logWatched,
            self.downloadWebStreams,
            self.removeWatchedOnFetch,
            self.playedAlwaysWatched,
            self.watchedLogFilepath,
            self.logDirPath,
            self.browserName,
            self.fetchLimitSingleSource]
        settingsStrings = [str(s) for s in settings]
        
        overlyComplicatedSettingsListList = []
        for i, name in enumerate(names):
            overlyComplicatedSettingsListList.append([name, settingsStrings[i]])
        overlyComplicatedSettingsLabels = ["Name                           ", "Value                                                         "]

        # ??? 
        # I blame asTable, needs fix for labels, but this could probably have been a list with a template for name and value like 
        # "| {name}{namePadding} - {setting}{settingPadding} |" or something equally dumb since there's no current column option for asTable, only rows
        return asTable(overlyComplicatedSettingsListList, overlyComplicatedSettingsLabels)
