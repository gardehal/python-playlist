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
    debug: bool = DEBUG

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
            _yt = YouTube(url)
            _title = _yt.title
        else:
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
            if(DEBUG): printS("Length of input \"existingIds\" (", len(existingIds), ") or \"indexList\" (", len(indexList), ") was 0.", color = colors["WARNING"])
            return []

        _result = []
        for i, _string in enumerate(input):
            if(limit != None and i >= limit):
                if(DEBUG): printS("Returning data before input ", _string, ", limit (", limit, ") reached.", color = colors["WARNING"])
                break
            
            if(_string[0] == "i"):  # starts with "i", like index of "i2" is 2
                if(not isNumber(_string[1])):
                    if(returnOnNonIds):
                        return _result
                    
                    printS("Argument ", _string, " is not a valid index format, must be \"i\" followed by an integer, like \"i0\". Argument not processed.", color = colors["FAIL"])
                    continue

                _index = int(float(_string[1]))
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
            printS(titles[i], color = colors["BOLD"])
            printS("No data.", color = colors["WARNING"], doPrint = len(dataList) == 0) 
            
            for j, entry in enumerate(dataList):
                _color = "WHITE" if j % 2 == 0 else "GREYBG"
                printS(entry, color = colors[_color]) 
                
        return True