import os
import re
from typing import Pattern

from dotenv import load_dotenv
from grdUtil.PrintUtil import printS
from grdUtil.BashColor import BashColor

from PlaylistService import PlaylistService
from QueueStreamService import QueueStreamService
from StreamSourceService import StreamSourceService

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")

class LegacyService():
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    lastFetchedIdRegex: Pattern[str] = None
    
    def __init__(self):
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.streamSourceService = StreamSourceService()
        self.lastFetchedIdRegex = re.compile("\s*\"lastFetchedId\":\s*\".*\",?", re.RegexFlag.IGNORECASE)
        
    def getFilePath(self, id: str) -> str:
        """
        Get file path from ID or None if no file was found.

        Args:
            id (str): ID of entity to get.
            
        Returns:
            str | None: Absolute file path.
        """
        
        if(self.playlistService.get(id) != None):
            return os.path.join(LOCAL_STORAGE_PATH, "Playlist", f"{id}.json")
        
        if(self.queueStreamService.get(id) != None):
            return os.path.join(LOCAL_STORAGE_PATH, "QueueStream", f"{id}.json")
        
        if(self.streamSourceService.get(id) != None):
            return os.path.join(LOCAL_STORAGE_PATH, "StreamSource", f"{id}.json")
        
        return None
        
    def runRefactorCheck(self) -> list[str]:
        """
        Check if refactor has been done on a selection of entities.

        Returns:
            list[str]: List of IDs of entities not refactored.
        """

        notRefactored = []
        
        # Check refactorLastFetchedId
        if(True):
            all = self.streamSourceService.getAll()
                
            firstId = all[0].id
            printS("Checking first: ", firstId, color = BashColor.WARNING, doPrint = DEBUG)
            with open(self.getFilePath(firstId), "r") as file:
                content = file.read()
                if(re.search(self.lastFetchedIdRegex, content)):
                    notRefactored.append(firstId)
                    
            lastId = all[-1].id
            printS("Checking last: ", lastId, color = BashColor.WARNING, doPrint = DEBUG)
            with open(self.getFilePath(lastId), "r") as file:
                content = file.read()
                if(re.match(self.lastFetchedIdRegex, content)):
                    notRefactored.append(lastId)
                    
            if(len(all) > 3):
                midId = all[int(len(all)/2)].id
                printS("DEBUG: runRefactorCheck - Checking mid: ", midId, color = BashColor.WARNING, doPrint = DEBUG)
                with open(self.getFilePath(midId), "r") as file:
                    content = file.read()
                    if(re.match(self.lastFetchedIdRegex, content)):
                        notRefactored.append(midId)
        
        return notRefactored
    
    def refactorLastFetchedId(self) -> bool:
        """
        Refactor all StreamSources in database to remove field lastFetchedId: str and add field lastFetchedIds: list[str].

        Returns:
            bool: Result of refactor.
        """

        all = self.streamSourceService.getAll()
        # get line in json with regex
        # replace line
        # save and repeat for each
        
        return True
        