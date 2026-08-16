import json
import os
import re
import urllib.request
from re import Pattern

import mechanize
from bs4 import BeautifulSoup
from grdException.ArgumentException import ArgumentException
from grdException.NotImplementedException import NotImplementedException
from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTimeAsNumber
from grdUtil.FileUtil import mkdir
from grdUtil.InputUtil import BashColor, sanitize
from grdUtil.PrintUtil import printD, printS
from jsonpath_ng import parse
import yt_dlp

from Settings import Settings


class DownloadService():
    settings: Settings = None
    
    def __init__(self):
        self.settings = Settings()
        
    def download(self, url: str, directory: str, fileExtension: str = "mp4", nameRegex: Pattern[str] = None, prefix: str = None) -> str:
        """
        Download stream given by URL.

        Args:
            url (str): URL to stream.
            directory (str): Directory (under self.settings.localStoragePath) to save downloaded content.
            fileExtension (str): File extension of stream.
            nameRegex (Pattern[str]): Regex to use for name.
            prefix (str): Any string to prefix filename with.

        Returns:
            str: Absolute path of file.
        """
        
        youtubeRegex = re.compile(r'(\.|\/)youtu(\.?)be(\.|\/)')
        odyseeRegex = re.compile(r'(\.|\/)odysee\.')
        
        if(youtubeRegex.search(url)):
            return self.downloadYoutube(url, directory, fileExtension, nameRegex, prefix)
        if(odyseeRegex.search(url)):
            return self.downloadOdysee(url, directory, fileExtension, nameRegex, prefix)
        
        raise NotImplementedException("No implementation for url: %s" % url)
        
    def getVideoPath(self, sourceName: str, name: str, fileExtension: str, nameRegex: Pattern[str] = None, prefix: str = None) -> str:
        """
        Get absolute path to download videos to, filename, with extension.

        Args:
            sourceName (str): Name of source.
            name (str): Name of stream.
            fileExtension (str): File extension of stream.
            nameRegex (Pattern[str]): Regex to use for name.
            prefix (str): Any string to prefix filename with.

        Returns:
            str: Absolute path of file.
        """
        
        directory = os.path.join(self.settings.localStoragePath, "video", sanitize(sourceName))
        mkdir(directory)
        
        useDefaultName = True
        customName = name
        if(nameRegex != None):
            useDefaultName = False
            customNameSearch = nameRegex.search(customName)
            if(len(customNameSearch.groups()) > 0):
                customNameMatch = customNameSearch.groups()[0]
                printS("Using Regex: \"", nameRegex, "\" on name \"", customName, "\". Result: \"", customNameMatch, "\"", color = BashColor.OKGREEN)
                customName = customNameMatch
            else:
                raise ArgumentException(f"The supplied Regex: \"{nameRegex}\" did not match anything in stream named \"{name}\". Could not determine desired name.")

        videoFilename = f"{customName}.{fileExtension}"
            
        if(useDefaultName):
            videoFilename = f"{str(getDateTimeAsNumber())}_{videoFilename}".replace(" ", "_").lower()
        
        if(prefix != None):
            videoFilename = f"{prefix}{videoFilename}"
    
        videoFilename = sanitize(videoFilename, mode = 3)
        return os.path.join(directory, videoFilename)

    def downloadYoutube(self, url: str, directory: str = "youtube", fileExtension: str = "mp4", nameRegex: Pattern[str] = None, prefix: str = None) -> str:
        """
        Download a Youtube video to given directory.

        Args:
            url (str): URL to video to download.
            directory (str): Directory (under self.settings.localStoragePath) to save downloaded content.
            fileExtension (str): File extension of stream.
            nameRegex (Pattern[str]): Regex to use for name.
            prefix (str): Any string to prefix filename with.

        Returns:
            str: Absolute path of file.
        """
        
        try:
            # Use yt_dlp instead of pytubefix
            ydl_opts = {
                'format': f'bestvideo[ext={fileExtension}]+bestaudio[ext=m4a]/best[ext={fileExtension}]/best',
                'noplaylist': True,
            }
            
            # We need the title first to use getVideoPath correctly
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                videoTitle = info.get('title', 'unknown_video')

            # Re-calculate path using existing logic to respect regex/prefix/sanitization
            videoPath = self.getVideoPath(directory, videoTitle, fileExtension, nameRegex, prefix)
            
            # Update opts with the actual target filename
            target_dir = os.path.dirname(videoPath)
            target_filename = os.path.basename(videoPath)
            ydl_opts['outtmpl'] = os.path.join(target_dir, target_filename)

            printS("Downloading video from ", url)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return videoPath
        except Exception as e:
            printS("Failed download video: ", e, color = BashColor.FAIL)
            return None

    def downloadOdysee(self, url: str, directory: str = "odysee", fileExtension: str = "mp4", nameRegex: Pattern[str] = None, prefix: str = None) -> str:
        """
        Download a Youtube video to given directory.

        Args:
            url (str): URL to video to download.
            directory (str): Directory (under self.settings.localStoragePath) to save downloaded content.
            fileExtension (str): File extension of stream.
            nameRegex (Pattern[str]): Regex to use for name.
            prefix (str): Any string to prefix filename with.

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
            br.open(url)
            html = br.response().read()
            document = BeautifulSoup(html, 'html.parser')
            scriptContent = document.find("script", { "type": "application/ld+json" })
            if(scriptContent == None):
                printS("No content was found for URL \"", url, "\". Please check that the URL is correct.", color = BashColor.FAIL)
                return None
            
            jsonString = scriptContent.text.strip()
            printD(jsonString, debug = (self.settings.debug and False))
            printD("Reading JSON...", debug = self.settings.debug)
            jsonData = json.loads(jsonString)
            videoTitle = parse("$.name").find(jsonData)[0].value
            fileUrl = parse("$.contentUrl").find(jsonData)[0].value
            printD("File URL: ", fileUrl, debug = self.settings.debug)
        except Exception as e:
            printS("Failed getting video: ", e, color = BashColor.FAIL)
            return None
        
        if(fileUrl == None):
            printS("Failed getting source video for ", url, color = BashColor.FAIL)
            return None
        
        if(videoTitle == None):
            videoTitle = "unknown_video"
            printS("Failed getting title, defaulting to ", videoTitle, color = BashColor.FAIL)
        
        videoPath = self.getVideoPath(directory, videoTitle, fileExtension, nameRegex, prefix)
        try:
            urllib.request.urlretrieve(fileUrl, videoPath) 
        except Exception as e:
            printS("Failed download video: ", e, color = BashColor.FAIL)
            return None

        return videoPath
