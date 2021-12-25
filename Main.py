import os
import sys
import json
import uuid
import mechanize
from typing import List, TypeVar
from enums.VideoSourceType import VideoSourceType
from model.Playlist import Playlist
from model.QueueVideo import QueueVideo
from model.VideoSource import VideoSource
from myutil.Util import *
from myutil.DateTimeObject import *
from pytube import Channel
from dotenv import load_dotenv

from model.VideoSourceCollection import VideoSourceCollection

T = TypeVar("T")

load_dotenv()
debug = False
settingsFilename = "settings.json"
sourcesFilename = "videoSourceCollection.json"
mainQueueFilename = "mainQueue.json"

os.system("") # Needed to "trigger" coloured text
helpFlags = ["-help", "-h"]
testFlags = ["-test", "-t"]
playFlags = ["-play", "-p"]
listQueueFlags = ["-list", "-l"]
addVideoFlags = ["-add", "-a"]
removeVideoFlags = ["-remove", "-rm", "-r"]
removeWatchedVideoFlags = ["-removewatched", "-rmw", "-rw"]
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
            
        Main.createLocalFilesIfNone()

        while argIndex < argC:
            arg = sys.argv[argIndex].lower()

            if(arg in helpFlags):
                Main.printHelp()

            elif(arg in testFlags):
                args = extractArgs(argIndex, argV)
                print("test")
                
                r = Main.readJsonFile(mainQueueFilename, Playlist)
                
                # if(r == None): r = Playlist()
                print(r)
                print(r.videoSource)
                print(type(r))
                print(Main.toDict(r))
                Main.writeToJsonFile(mainQueueFilename, r)

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
            
    def createLocalFilesIfNone() -> bool:
        """
        Create local files used for storing settings, video ques, sources etc.

        Returns:
            bool: success = true
        """
        
        files = [settingsFilename, sourcesFilename, mainQueueFilename]
        
        for file in files:
            open(file, "a")
            
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
        
    def toDict(obj: object) -> dict:
        """
        Converts objects to dictionaries.
        Source: https://www.codegrepper.com/code-examples/whatever/python+nested+object+to+dict

        Args:
            obj (object): object to convert

        Returns:
            dict: dictionary of input object
        """
        
        if not  hasattr(obj,"__dict__"):
            return obj
        
        result = {}
        for key, val in obj.__dict__.items():
            if key.startswith("_"):
                continue
            
            element = []
            if isinstance(val, list):
                for item in val:
                    element.append(Main.toDict(item))
            else:
                element = Main.toDict(val)
                
            result[key] = element
            
        return result
    
    def toJson(obj: object) -> str:
        """
        Converts objects to JSON though dictionaries.

        Args:
            obj (object): object to convert

        Returns:
            str: JSON string
        """
        
        dict = Main.toDict(obj)
        return json.dumps(dict, default=str)
    
    def writeToJsonFile(filepath: str, obj: object) -> bool:
        """
        Writes object obj to a JSON format in file from filepath.

        Args:
            filepath (str): path to file to store JSON in
            obj (object): object to save

        Returns:
            bool: true = success
        """
        
        asDict = Main.toDict(obj)
        with open(filepath, "w") as file:
            json.dump(asDict, file, indent=4, default=str)
            
        return True
    
    def readJsonFile(filepath: str, typeT: T) -> T:
        """
        Opens and reads a JSON formatted file, returning object of type T.

        Args:
            filepath (str): path to file to read JSON from
            typeT (T): object to convert to

        Returns:
            T or None: object from JSON file, if file is empty: None
        """
        
        fileContent = open(filepath, "r").read()
        if(len(fileContent) < 2):
            return None
        else:
            return Main.fromJson(fileContent, typeT)
    
    def fromJson(jsonStr: str, typeT: T) -> T:
        """
        Converts JSON to an object T.

        Args:
            str (str): string to convert
            typeT (T): object to convert to

        Returns:
            T: object from JSON
        """
        
        jsonDict = json.loads(jsonStr)
        asObj = typeT(**jsonDict)

        for fieldName in dir(asObj):
            # Skip default fields and functions
            if(fieldName.startswith('__') or callable(getattr(asObj, fieldName))):
                continue

            field = getattr(asObj, fieldName)
            fieldType = type(field)
            typeTField = getattr(typeT(), fieldName)


            print(type(field))
            print(field)
            print(typeTField)

            if("uuid" in str(fieldType) or "datetime" in str(fieldType)):
                continue
            elif(isinstance(fieldType, list)):
                print("--------------list")
                objList = []
                for listDict in field:
                    if("VideoSource" in str(typeTField)):
                        print(listDict)
                        objList.append(VideoSource(**listDict))
                    #else: other objects

                setattr(asObj, fieldName, objList)
            elif(isinstance(field, dict)):
                obj = {}
                if("VideoSource" in str(typeTField)):
                    obj = VideoSource(**field)
                
                setattr(asObj, fieldName, obj)

        return asObj
        
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
        
        sourceCollection = Main.readJsonFile(sourcesFilename, VideoSourceCollection)
        queue = Main.readJsonFile(mainQueueFilename, Playlist)
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
    
    def fetchYoutube(videoSource: VideoSource, batchSize: int, takeAfter: DateTimeObject, takeBefore: DateTimeObject) -> List[QueueVideo]:
        """
        Fetch videos from YouTube

        Args:
            batchSize (int): number of videos to check at a time, unrelated to max videos that will be read
            takeAfter (DateTimeObject): limit to take video after
            takeBefore (DateTimeObject): limit to take video before

        Returns:
            List[QueueVideo]: List of QueueVideo
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
            
            newVideos.append(QueueVideo(yt.title, yt.watch_url, None, now, videoSource.name))
            
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