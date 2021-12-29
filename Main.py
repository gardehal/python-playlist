import os
import sys
from uuid import uuid4
import mechanize
from typing import List
from PlaylistService import PlaylistService
from enums.VideoSourceType import VideoSourceType
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from model.VideoSource import VideoSource
from myutil.Util import *
from JsonUtil import *
from LocalJsonRepository import *
from myutil.DateTimeObject import *
from pytube import Channel
from dotenv import load_dotenv

from model.VideoSourceCollection import VideoSourceCollection

load_dotenv()
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")

debug = False
sourcesFilename = "videoSourceCollection.json"
mainQueueFilename = "mainQueue.json"

os.system("") # Needed to "trigger" coloured text
# General
helpFlags = ["-help", "-h"]
testFlags = ["-test", "-t"]
# Playlist
addPlaylistFlags = ["-addplaylist", "-apl", "-ap"]
removePlaylistFlags = ["-removeplaylist", "-rpl", "-rp"]
listQueueFlags = ["-listplaylist", "-lpl", "-lp"]
playFlags = ["-play", "-p"]
# Video
addVideoFlags = ["-add", "-a"]
removeVideoFlags = ["-remove", "-rm", "-r"]
listQueueFlags = ["-list", "-l"]
removeWatchedVideoFlags = ["-removewatched", "-rmw", "-rw"]
# Sources
listSourcesFlags = ["-listsources", "-ls"]
addSourcesFlags = ["-addsource", "-as"]
removeSourceFlags = ["-removesource", "-rms", "-rs"]
fetchSourceFlags = ["-fetch", "-f", "-update", "-u"]

class Main:
    def main():
        argC = len(sys.argv)
        argV = sys.argv
        argIndex = 1

        if(argC < 2):
            Main.printHelp()
            
        Main.mkfiles(sourcesFilename, mainQueueFilename, WATCHED_LOG_FILEPATH)

        while argIndex < argC:
            arg = sys.argv[argIndex].lower()

            if(arg in helpFlags):
                Main.printHelp()

            elif(arg in testFlags):
                args = extractArgs(argIndex, argV)
                printS("Test", color = colors["OKBLUE"])
                
                quit()

            elif(arg in listSourcesFlags):
                args = extractArgs(argIndex, argV)
                
                sources = Main.getSources()
                
                if(len(sources.sources) > 0):
                    for i, source in enumerate(sources.sources):
                        print(f"{i+1}: {source.name} - {source.url if source.isWebSource else source.directory}")
                else:
                    printS("No sources found in the sources file.")

                argIndex += 1
                continue

            elif(arg in addSourcesFlags):
                args = extractArgs(argIndex, argV)
                
                sourcesAdded = Main.addSources(args)
                if(sourcesAdded != None and sourcesAdded > 0):
                    printS("Added ", sourcesAdded, " new sources", color=colors["OKGREEN"])

                argIndex += len(args) + 1
                continue

            elif(arg in fetchSourceFlags):
                args = extractArgs(argIndex, argV)
                
                sourcesAdded = Main.fetchVideoSources(10)
                if(sourcesAdded != None and sourcesAdded > 0):
                    printS("Fetched ", sourcesAdded, " new videos to list ", "listname", color=colors["OKGREEN"])

                argIndex += len(args) + 1
                continue

            # Invalid, inform and quit
            else:
                printS("Argument not recognized: \"", arg, "\", please see documentation or run with \"-help\" for help.", color=colors["WARNING"])

            argIndex += 1
            
    def mkfiles(*args) -> bool:
        """
        Create local files used for storing settings, video ques, sources etc.

        Args:
            args (list): paths+filenames to create

        Returns:
            bool: success = true
        """
        
        for filepath in args:
            try:
                if(not os.path.exists(os.path.dirname(filepath))):
                    os.makedirs(os.path.dirname(filepath))
            except OSError as exc: # Guard against race condition
                continue

            file = open(filepath, "a")
            file.close()
            
        return True

    def sourceToVideoSourceType(source: str) -> VideoSourceType:
        """
        Get VideoSourceType from string (path or url).

        Args:
            source (str): path or url to source of videos

        Returns:
            VideoSourceType: VideoSourceType or None
        """
        
        if(os.path.isdir(source)):
            return VideoSourceType.DICTIONARY
        if("https://youtu.be" in source or "https://www.youtube.com" in source):
            return VideoSourceType.YOUTUBE
        
        return None
        
    def addSources(sources: List[str]) -> int:
        """
        Add video source(s) to list of watched sources.

        Args:
            sources (List[str]): list of sources to add

        Returns:
            int: number of added sources
        """
        
        now = DateTimeObject().now
        updatedSourcesJson = Main.readJsonFile(sourcesFilename, VideoSourceCollection)
        if(updatedSourcesJson == None): updatedSourcesJson = VideoSourceCollection("New source", [], now)
        
        addedSources = 0
        for source in sources:
            isUrl = validators.url(source)
            url = source if isUrl else None
            dir = source if os.path.exists(source) else None
            if(Main.sourceToVideoSourceType(source) == None):
                printS("The source: ", source, "is not a valid supported website or directory path.", color=colors["FAIL"])
                continue
            
            name = f"New source - {source}"
            if(isUrl):
                br = mechanize.Browser()
                br.open(source)
                name = br.title()
                br.close()
            else:
                name = os.path.basename(source)
                # TODO
            
            # TODO vars for non-web sources, non-youtube
            newSource = VideoSource(name, url, dir, isUrl, VideoSourceType.YOUTUBE.name, True, now, now)
            updatedSourcesJson.sources.append(Main.toDict(newSource))
            addedSources += 1
            
        Main.writeToJsonFile(sourcesFilename, updatedSourcesJson)        
        return addedSources     
    
    def fetchVideoSources(batchSize: int = 10, takeAfter: DateTimeObject = None, takeBefore: DateTimeObject = None) -> int:
        """
        Fetch new videos from watched sources, adding them in chronological order.

        Args:
            batchSize (int): number of videos to check at a time, unrelated to max videos that will be read
            takeAfter (DateTimeObject): limit to take video after
            takeBefore (DateTimeObject): limit to take video before

        Returns:
            int: number of videos added
        """
        
        sourceCollection = JsonUtil.readJsonFile(sourcesFilename, VideoSourceCollection)
        queue = JsonUtil.readJsonFile(mainQueueFilename, Playlist)
        now = DateTimeObject().now

        print("quitting")
        quit()

        if(sourceCollection == None):
            printS("Could not find any sources. Use flag -addsource [source] to add a source to fetch from.", color=colors["ERROR"])
            return 0
        if(queue == None): queue = Playlist("Main playlist", [], sourceCollection.name, sourceCollection.id, now, 0)
        
        lastFetch = DateTimeObject().fromString("2021-12-18 00:00:00")
        # lastFetch = queue.lastUpdated
        newVideos = []
        for source in sourceCollection.sources:
            if(not source.enableFetch):
                continue

            if(source.isWebSource):
                if(Main.sourceToVideoSourceType(source.url)):
                    newVideos += Main.fetchYoutube(source, batchSize, lastFetch, takeBefore)
                else:  
                    # TODO handle other sources
                    continue
            else:
                # TODO handle directory sources
                continue
        
        printS(queue.videos)
        printS("old vid len ", len(queue.videos))
        for video in newVideos:
            queue.videos.append(Main.toDict(video))
        printS("new vid len ", len(queue.videos))
            
        queue.lastUpdated = now
        Main.writeToJsonFile(mainQueueFilename, queue)     
        return len(newVideos)
    
    def fetchYoutube(videoSource: VideoSource, batchSize: int, takeAfter: DateTimeObject, takeBefore: DateTimeObject) -> List[QueueStream]:
        """
        Fetch videos from YouTube

        Args:
            batchSize (int): number of videos to check at a time, unrelated to max videos that will be read
            takeAfter (DateTimeObject): limit to take video after
            takeBefore (DateTimeObject): limit to take video before

        Returns:
            List[QueueStream]: List of QueueStream
        """
        
        if(debug): printS("fetchYoutube start, fetching channel source")
        now = DateTimeObject().now
        channel = Channel(videoSource.url)
        # Todo fetch batches using batchSize of videos instead of all 3000 videos in some cases taking 60 seconds+ to load
        
        if(channel == None or channel.channel_name == None):
            printS("Channel ", videoSource.name, " ( ", videoSource.url, " ) could not be found or is not valid. Please remove it and add it back.", color=colors["ERROR"])
            return []
        
        if(debug): printS("Fetching videos from ", channel.channel_name)
        if(len(channel.video_urls) < 1):
            printS("Channel ", channel.channel_name, " has no videos.", color=colors["WARNING"])
            return []
        
        newVideos = []
        for i, yt in enumerate(channel.videos):
            published = DateTimeObject().fromDatetime(yt.publish_date)
                      
            if(takeAfter != None and published.isoWithMilliAsNumber < takeAfter.isoWithMilliAsNumber):
                break
            if(takeBefore != None and published.isoWithMilliAsNumber > takeBefore.isoWithMilliAsNumber):
                continue
            
            newVideos.append(QueueStream(yt.title, yt.watch_url, True, None, now, videoSource.id))
            
            if(i > 10):
                printS("WIP: Cannot get all videos. Taking last ", len(newVideos))
                break
        
        return newVideos

    def printHelp():
        """
        A simple console print that informs user of program arguments.

        Returns:
            None: None
        """

        print("--- Help ---")
        print("Arguments marked with ? are optional.")
        print("All arguments that triggers a function start with dash(-).")
        print("All arguments must be separated by space only.")
        print("\n")

        printS(helpFlags, ": Prints this information about input arguments.")
        printS(testFlags, ": A method of calling experimental code (when you want to test if something works).")
        # printS(testFlags, " + [args]: Details.")
        # printS("\t", testSwitches, " + [args]: Details.")

        printS(playFlags, ": Starts playing the queue.")
        printS(listQueueFlags, ": List videos in queue.")
        printS(addVideoFlags, " + [1+ URLs or paths to files]: Add videos to queue.")
        printS(removeVideoFlags, " + [index]: Remove videos from queue.")
        printS(listSourcesFlags, ": List watched sources.")
        printS(addSourcesFlags, " + [1+ URLs or paths to directories]: Adds a video source to list of watched sources.")
        printS(removeSourceFlags, " + [1+ URLs or paths to directories]: Removes video source(s) from list of watched sources.")
        printS(fetchSourceFlags, ": Update queue with videos from list of watched sources.")
        
if __name__ == "__main__":
    Main.main()