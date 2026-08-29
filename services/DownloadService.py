import json
import os
import re
import urllib.request
from re import Pattern
import mechanize
import yt_dlp
from pytubefix import YouTube
from jsonpath_ng import parse
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB
from bs4 import BeautifulSoup

from grdException.ArgumentException import ArgumentException
from grdException.NotImplementedException import NotImplementedException
from grdUtil.BashColor import BashColor
from grdUtil.DateTimeUtil import getDateTimeAsNumber
from grdUtil.FileUtil import mkdir
from grdUtil.InputUtil import BashColor, sanitize
from grdUtil.PrintUtil import printD, printS

from Settings import Settings


class DownloadService():
    settings: Settings = None
    
    def __init__(self):
        self.settings = Settings()
        
    def download(self, url: str, directory: str, fileExtension: str = "mp4", nameRegex: Pattern[str] = None, prefix: str = None, audioOnly: bool = False) -> str:
        """
        Download stream given by URL.

        Args:
            url (str): URL to stream.
            directory (str): Directory (under self.settings.localStoragePath) to save downloaded content.
            fileExtension (str): File extension of stream.
            nameRegex (Pattern[str]): Regex to use for name.
            prefix (str): Any string to prefix filename with.
            audioOnly (bool): Download as audio.

        Returns:
            str: Absolute path of file.
        """
        
        youtubeRegex = re.compile(r'(\.|\/)youtu(\.?)be(\.|\/)')
        odyseeRegex = re.compile(r'(\.|\/)odysee\.')
        
        if(youtubeRegex.search(url)):
            return self.downloadYoutube(url, directory, fileExtension, nameRegex, prefix, audioOnly)
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

    def downloadYoutube(self, url: str, directory: str = "youtube", fileExtension: str = "mp4", nameRegex: Pattern[str] = None, prefix: str = None, audioOnly: bool = False) -> str:
        """
        Download a Youtube video to given directory.

        Args:
            url (str): URL to video to download.
            directory (str): Directory (under self.settings.localStoragePath) to save downloaded content.
            fileExtension (str): File extension of stream.
            nameRegex (Pattern[str]): Regex to use for name.
            prefix (str): Any string to prefix filename with.
            audioOnly (bool): Download as audio.

        Returns:
            str: Absolute path of file.
        """
        
        try:
            # TODO yt-dlp has issues getting all videos, replace pytubefix parked for now
            # ydl_opts = {
            #     'format': f'bestvideo[ext={fileExtension}]+bestaudio[ext=m4a]/best[ext={fileExtension}]/best',
            #     'noplaylist': True,
            # }
            
            # with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            #     info = ydl.extract_info(url, download=False)
            #     videoTitle = info.get('title', 'unknown_video')

            # target_dir = os.path.dirname(videoPath)
            # target_filename = os.path.basename(videoPath)
            # ydl_opts['outtmpl'] = os.path.join(target_dir, target_filename)

            # printS("Downloading video from ", url)
            # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            #     ydl.download([url])

            # videoPath = self.getVideoPath(directory, videoTitle, fileExtension, nameRegex, prefix)

            youtube = YouTube(url)
            printS("Downloading video from ", url)
            videoPath = self.getVideoPath(directory, youtube.title, fileExtension, nameRegex, prefix)
            path = os.sep.join(videoPath.split(os.sep)[0:-1])
            name = videoPath.split(os.sep)[-1]

            video = youtube.streams.filter(progressive = True, file_extension = fileExtension)
            if(audioOnly):
                video.order_by("resolution").desc().first().download(path, name).get_audio_only()
                # TODO more emtadata, mainly track number. album (playlist name) and year would be good to, but relies on info from playlist or track names
                # Alternativly, give user a modal when clicking this, make them input a clean artist, album, year, etc., do not set if fields are blank
                self.setMp3Metadata(videoPath, youtube.title, youtube.channel_name)
            else:
                video.order_by("resolution").desc().first().download(path, name) 
            
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

    def setMp3Metadata(self, file_path: str, title: str, artist: str):
        audio = MP3(file_path, ID3=ID3)

        if audio.tags is None:
            audio.add_tags()

        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        # audio.tags.add(TALB(encoding=3, text=album))
        # year
        # track #

        audio.save()
