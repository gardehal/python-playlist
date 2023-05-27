import json
import os

import mechanize
import urllib.request
from bs4 import BeautifulSoup
from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTimeAsNumber
from grdUtil.FileUtil import mkdir
from grdUtil.InputUtil import sanitize
from grdUtil.PrintUtil import printD, printS
from jsonpath_ng import jsonpath, parse
from pytube import YouTube

from Settings import Settings


class DownloadService():
    settings: Settings = None
    def __init__(self):
        self.settings = Settings()
        
    def getVideoPath(self, sourceName: str, name: str, fileExtension: str) -> str:
        """
        Get absolute path to download videos to, filename, with extension.

        Args:
            sourceName (str): Name of source.
            name (str): Name of stream.
            fileExtension (str): File extension of stream.

        Returns:
            str: Absolute path of file.
        """
        
        directory = os.path.join(self.settings.localStoragePath, "video", sourceName)
        mkdir(directory)
        
        videoFilename = f"{str(getDateTimeAsNumber())}_{sanitize(name)}.{fileExtension}".replace(" ", "_").lower()
    
        return os.path.join(directory, videoFilename)

    def downloadYoutube(self, url: str, fileExtension: str = "mp4") -> str:
        """
        Download a Youtube video to given directory.

        Args:
            url (str): URL to video to download.
            fileExtension (str): File extension of stream.

        Returns:
            str: Absolute path of file.
        """
        
        youtube = YouTube(url)
        printD("Downloading video from ", url)
        videoPath = self.getVideoPath("youtube", youtube.title, fileExtension)
        youtube.streams.filter(progressive = True, file_extension = fileExtension).order_by("resolution").desc().first().download(videoPath)
                
        return videoPath

    def downloadOdysee(self, url: str, fileExtension: str = "mp4") -> str:
        """
        Download a Youtube video to given directory.

        Args:
            url (str): URL to video to download.
            fileExtension (str): File extension of stream.

        Returns:
            str: Absolute path of file.
        """
        
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        fileUrl = None
        try:
            br.open(url)
            html = br.response().read()
            document = BeautifulSoup(html, 'html.parser')
            jsonString = document.find("script", { "type": "application/ld+json" }).text.strip()
            jsonData = json.loads(jsonString)
            contentUrlExpression = parse("$.contentUrl")
            fileUrl = contentUrlExpression.find(jsonData)[0].value
        except:
            printS("Failed getting video for ", url, color = BashColor.FAIL)
            return "" # throw x
        
        if(fileUrl == None):
            printS("Failed getting URL to video for ", url, color = BashColor.FAIL)
            return "" # throw x
        
        printD("Downloading video from ", url)
        videoPath = self.getVideoPath("odysee", "test", fileExtension)
        urllib.request.urlretrieve(fileUrl, videoPath) 
                
        return videoPath
    