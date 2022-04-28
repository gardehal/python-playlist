import os
import random
import re
from turtle import update
from typing import Pattern

from dotenv import load_dotenv
from grdUtil.PrintUtil import printS, printStack
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
    stringValueRegex: Pattern[str] = None
    
    def __init__(self):
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.streamSourceService = StreamSourceService()
        self.lastFetchedIdRegex = re.compile("\s*\"lastFetchedId\":\s*\".*\",?", re.RegexFlag.IGNORECASE)
        self.stringValueRegex = re.compile("\s*\".*\":\s*\"(.*)\",?", re.RegexFlag.IGNORECASE)
        
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
        
        if(self.streamSourceService.get(id) != None):
            return os.path.join(LOCAL_STORAGE_PATH, "StreamSource", f"{id}.json")
        
        if(self.queueStreamService.get(id) != None):
            return os.path.join(LOCAL_STORAGE_PATH, "QueueStream", f"{id}.json")
        
        return None
        
    def refactorCheckLastFetchedId(self, checkDivisor: int = 10) -> list[str]:
        """
        Check if refactor has been done on a selection of entities.

        Args:
            checkDivisor (int): Divisor of len(self.streamSourceService.getAll())/x to check. Default 10.

        Returns:
            list[str]: List of IDs of entities not refactored.
        """

        notRefactored = []
        all = self.streamSourceService.getAll()
        nChecks = int(len(all) / checkDivisor)
        indicesChecked = []
        
        for i in range(nChecks):
            index = 0
            while 1:
                index = random.randrange(0, len(all))
                if(index not in indicesChecked):
                    break
            
            id = all[index].id
            printS("DEBUG: refactorCheckLastFetchedId - Checking ", (i+1), "/", nChecks, ": ", id, color = BashColor.WARNING, doPrint = DEBUG)
            with open(self.getFilePath(id), "r") as file:
                content = file.read()
                if(re.search(self.lastFetchedIdRegex, content)):
                    notRefactored.append(id)
        
        return notRefactored
    
    def refactorLastFetchedId(self) -> list[str]:
        """
        Refactor all StreamSources in database to remove field lastFetchedId: str and add field lastFetchedIds: list[str].

        Returns:
            list[str]: IDs of entities refactored.
        """

        all = self.streamSourceService.getAll()
        result = []
        for item in all:
            updatedContent = []
            with open(self.getFilePath(item.id), "r") as file:
                content = file.readlines()
                
                for line, i in enumerate(content):
                    if(not re.search(self.lastFetchedIdRegex, line)):
                        continue
                    
                    value = ""
                    content[i] = ""
                    updatedContent = content
                    break
                    
            if(len(updatedContent) == 0):
                continue
                
            try:    
                with open(self.getFilePath(item.id), "w") as file:
                    file.writelines(updatedContent)
                result.append(item.id)
            except:
                printStack()
        
        return result
        