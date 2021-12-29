import os
import sys
from uuid import uuid4
from typing import List
from FetchService import FetchService
from PlaylistService import PlaylistService
from StreamSourceService import StreamSourceService
from enums.StreamSourceType import StreamSourceType
from model.Playlist import Playlist
from model.QueueStream import QueueStream
from myutil.Util import *
from JsonUtil import *
from LocalJsonRepository import *
from myutil.DateTimeObject import *
from dotenv import load_dotenv

from model.StreamSource import StreamSource
os.system("") # Needed to "trigger" coloured text

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")

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
            
        Main.makeFiles(WATCHED_LOG_FILEPATH)

        while argIndex < argC:
            arg = sys.argv[argIndex].lower()

            if(arg in helpFlags):
                Main.printHelp()

            elif(arg in testFlags):
                args = extractArgs(argIndex, argV)
                printS("Test", color = colors["OKBLUE"])
                
                if(0):
                    fs = FetchService()
                    sss = StreamSourceService()
                    id = "d061d474-c79b-4008-a9cf-a003c03e5db3"
                    # print(sss.add(StreamSource("mocked", "https://www.youtube.com/channel/UCFtc3XdXgLFwhlDajMGK69w", True, 2, True)))
                    # print(fs.fetch(id))

                if(1):
                    e = QueueStream()
                    e.isWeb = True
                    e.uri = "https://youtu.be/KMtrY6lbjcY"
                    id = "d061d474-c79b-4008-a9cf-a003c03e5db3"

                    # r = LocalJsonRepository(QueueStream, True, "test")
                    # print(r.add(e))

                    s = PlaylistService()
                    # print(s.addStreams(id, [e]))
                    print(s.playCmd(id))

                if(False):
                    e = QueueStream()
                    id = "28815709-b340-4378-b443-95317a897073"

                    r = LocalJsonRepository(QueueStream, True, "test")
                    # r.add(e)

                    i = r.get(id)
                    # print(JsonUtil.toDict(i))

                    all = r.getAll()
                    # print(all)

                    # r.remove(id)

                    ii = i
                    ii.videoName = "New name"
                    r.update(ii)

                if(False):
                    s = PlaylistService(True, "test")

                    e = Playlist("Test")
                    id = "d061d474-c79b-4008-a9cf-a003c03e5db3"
                    print(s.add(e))

                    q = QueueStream("q")
                    q.id = str(uuid4())
                    qq = QueueStream("qq")

                    # print(s.addStreams(id, [q, qq]))
                    # print(s.removeStreams(id, [0, 111, 4]))
                    # print(s.moveStream(id, 7, 4))
                    # e.id = "91a5f9ad-f68c-4dda-aaac-c9ee464dcce0"
                    # e.name = "should update"
                    # print(s.addOrUpdate(e))

                    # s.playCmd(id)
                    
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
                
                sourcesAdded = Main.fetchStreamSources(10)
                if(sourcesAdded != None and sourcesAdded > 0):
                    printS("Fetched ", sourcesAdded, " new videos to list ", "listname", color=colors["OKGREEN"])

                argIndex += len(args) + 1
                continue

            # Invalid, inform and quit
            else:
                printS("Argument not recognized: \"", arg, "\", please see documentation or run with \"-help\" for help.", color=colors["WARNING"])

            argIndex += 1
            
    def makeFiles(*args) -> bool:
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

    def sourceToStreamSourceType(source: str) -> StreamSourceType:
        """
        Get StreamSourceType from string (path or url).

        Args:
            source (str): path or url to source of videos

        Returns:
            StreamSourceType: StreamSourceType or None
        """
        
        if(os.path.isdir(source)):
            return StreamSourceType.DICTIONARY
        if("https://youtu.be" in source or "https://www.youtube.com" in source):
            return StreamSourceType.YOUTUBE
        
        return None 

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