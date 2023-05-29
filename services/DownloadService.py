import json
import os
import re
import sys
import urllib.request

import mechanize
from bs4 import BeautifulSoup
from grdException.NotImplementedException import NotImplementedException
from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTimeAsNumber
from grdUtil.FileUtil import mkdir
from grdUtil.InputUtil import BashColor, sanitize
from grdUtil.PrintUtil import printD, printS
from jsonpath_ng import jsonpath, parse
from pytube import YouTube

from Settings import Settings


class DownloadService():
    settings: Settings = None
    
    def __init__(self):
        self.settings = Settings()
        
    def download(self, url: str, directory: str, fileExtension: str = "mp4") -> str:
        """
        Download stream given by URL.

        Args:
            url (str): URL to stream.
            directory (str): Directory (under self.settings.localStoragePath) to save downloaded content.
            fileExtension (str): File extension of stream.

        Returns:
            str: Absolute path of file.
        """
        
        youtubeRegex = re.compile(r'(\.|\/)youtu(\.?)be(\.|\/)')
        odyseeRegex = re.compile(r'(\.|\/)odysee\.')
        
        if(youtubeRegex.search(url)):
            return self.downloadYoutube(url, directory, fileExtension)
        if(odyseeRegex.search(url)):
            return self.downloadOdysee(url, directory, fileExtension)
        
        raise NotImplementedException("No implementation for url: %s" % url)
        
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
        
        source = sanitize(sourceName).replace(" ", "_").lower()
        directory = os.path.join(self.settings.localStoragePath, "video", source)
        mkdir(directory)
        
        videoFilename = f"{str(getDateTimeAsNumber())}_{sanitize(name)}.{fileExtension}".replace(" ", "_").lower()
    
        return os.path.join(directory, videoFilename)

    def downloadYoutube(self, url: str, directory: str = "youtube", fileExtension: str = "mp4") -> str:
        """
        Download a Youtube video to given directory.

        Args:
            url (str): URL to video to download.
            directory (str): Directory (under self.settings.localStoragePath) to save downloaded content.
            fileExtension (str): File extension of stream.

        Returns:
            str: Absolute path of file.
        """
        
        youtube = YouTube(url)
        printS("Downloading video from ", url)
        videoPath = self.getVideoPath(directory, youtube.title, fileExtension)
        path = "/".join(videoPath.split("/")[0:-1])
        name = videoPath.split("/")[-1]
        try:
            youtube.streams.filter(progressive = True, file_extension = fileExtension).order_by("resolution").desc().first().download(path, name)
        except Exception as e:
            printS("Failed download video: ", e, color = BashColor.FAIL)
            return None
                
        return videoPath

    def downloadOdysee(self, url: str, directory: str = "odysee", fileExtension: str = "mp4") -> str:
        """
        Download a Youtube video to given directory.

        Args:
            url (str): URL to video to download.
            directory (str): Directory (under self.settings.localStoragePath) to save downloaded content.
            fileExtension (str): File extension of stream.

        Returns:
            str: Absolute path of file.
        """
        
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        videoTitle = None
        fileUrl = None
        try:
            printS("Fetching data for video ", url)
            sys.stdout.flush()
            br.open(url)
            html = br.response().read()
            document = BeautifulSoup(html, 'html.parser')
            scriptContent = document.find("script", { "type": "application/ld+json" })
            if(scriptContent == None):
                printS("No content was found for URL \"", url, "\". Please check that the URL is correct.", color = BashColor.FAIL)
                sys.stdout.flush()
                return None
            
            jsonString = scriptContent.text.strip()
            printD(jsonString, debug = (self.settings.debug and False))
            printD("Reading JSON...", debug = self.settings.debug)
            sys.stdout.flush()
            jsonData = json.loads(jsonString)
            videoTitle = parse("$.name").find(jsonData)[0].value
            fileUrl = parse("$.contentUrl").find(jsonData)[0].value
            printD("File URL: ", fileUrl, debug = self.settings.debug)
            sys.stdout.flush()
        except Exception as e:
            printS("Failed getting video: ", e, color = BashColor.FAIL)
            return None
        
        if(fileUrl == None):
            printS("Failed getting source video for ", url, color = BashColor.FAIL)
            return None
        
        if(videoTitle == None):
            videoTitle = "unknown_video"
            printS("Failed getting title, defaulting to ", videoTitle, color = BashColor.FAIL)
        
        videoPath = self.getVideoPath(directory, videoTitle, fileExtension)
        sys.stdout.flush()
        try:
            urllib.request.urlretrieve(fileUrl, videoPath) 
        except Exception as e:
            printS("Failed download video: ", e, color = BashColor.FAIL)
            sys.stdout.flush()
            return None

        return videoPath
    