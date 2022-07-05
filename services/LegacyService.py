import os
import random
import re
from typing import Pattern

from grdUtil.BashColor import BashColor
from grdUtil.PrintUtil import printD, printStack
from Settings import Settings

from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.StreamSourceService import StreamSourceService


class LegacyService():
    settings: Settings = None
    playlistService: PlaylistService = None
    queueStreamService: QueueStreamService = None
    streamSourceService: StreamSourceService = None
    lastFetchedIdRegex: Pattern[str] = None
    stringValueRegex: Pattern[str] = None
    
    def __init__(self):
        self.settings = Settings()
        self.playlistService = PlaylistService()
        self.queueStreamService = QueueStreamService()
        self.streamSourceService = StreamSourceService()
        self.lastFetchedIdRegex = re.compile("\s*\"lastFetchedId\":\s*\"?.*\"?,?", re.RegexFlag.IGNORECASE)
        self.stringValueRegex = re.compile("\s*\".*\":\s*\"(.*)\",?", re.RegexFlag.IGNORECASE)
        self.nullValueRegex = re.compile("\s*\".*\":\s*null,?", re.RegexFlag.IGNORECASE)
        
    def getFilePath(self, id: str) -> str:
        """
        Get file path from ID or None if no file was found.

        Args:
            id (str): ID of entity to get.
            
        Returns:
            str | None: Absolute file path.
        """
        
        if(self.playlistService.get(id) != None):
            return os.path.join(self.settings.localStoragePath, "Playlist", f"{id}.json")
        
        if(self.streamSourceService.get(id) != None):
            return os.path.join(self.settings.localStoragePath, "StreamSource", f"{id}.json")
        
        if(self.queueStreamService.get(id) != None):
            return os.path.join(self.settings.localStoragePath, "QueueStream", f"{id}.json")
        
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
            printD("Checking ", (i+1), "/", nChecks, ": ", id, color = BashColor.WARNING, debug = self.settings.debug)
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

        all = self.streamSourceService.getAll()[:1]
        result = []
        for item in all:
            updatedContent = []
            with open(self.getFilePath(item.id), "r") as file:
                content = file.readlines()
                
                for i, line in enumerate(content):
                    print(line)
                    if(not re.search(self.lastFetchedIdRegex, line)):
                        continue
                    
                    regexSearch = re.search(self.stringValueRegex, line)
                    value = regexSearch[1] if(regexSearch != None) else None
                    
                    updatedLine = line
                    updatedLine = updatedLine.replace("lastFetchedId", "lastFetchedIds")
                    if(value == None or len(value) == 0):
                        updatedLine = updatedLine.replace(f"null", f"[]")
                    else:
                        updatedLine = updatedLine.replace(f"\"{value}\"", f"[\"{value}\"]")
                        
                    content[i] = updatedLine
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
        