import os
import sys

from dotenv import load_dotenv
from myutil.Util import *

from enums.StreamSourceType import StreamSourceType
from FetchService import FetchService
from PlaylistService import PlaylistService
from StreamSourceService import StreamSourceService

os.system("") # Needed to "trigger" coloured text

load_dotenv()
DEBUG = eval(os.environ.get("DEBUG"))
LOCAL_STORAGE_PATH = os.environ.get("LOCAL_STORAGE_PATH")
LOG_WATCHED = eval(os.environ.get("LOG_WATCHED"))
DOWNLOAD_WEB_STREAMS = eval(os.environ.get("DOWNLOAD_WEB_STREAMS"))
REMOVE_WATCHED_ON_FETCH = eval(os.environ.get("REMOVE_WATCHED_ON_FETCH"))
PLAYED_ALWAYS_WATCHED = eval(os.environ.get("PLAYED_ALWAYS_WATCHED"))
WATCHED_LOG_FILEPATH = os.environ.get("WATCHED_LOG_FILEPATH")
BROWSER_BIN = os.environ.get("BROWSER_BIN")

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
# Meta
listSettingsFlags = ["-settings", "-secrets", "-s"]

class Main:
    def main():
        argC = len(sys.argv)
        argV = sys.argv
        argIndex = 1

        if(argC < 2):
            Main.printHelp()
            
        makeFiles(WATCHED_LOG_FILEPATH)

        while argIndex < argC:
            arg = sys.argv[argIndex].lower()

            if(arg in helpFlags):
                Main.printHelp()

            elif(arg in testFlags):
                args = extractArgs(argIndex, argV)
                printS("Test", color = colors["OKBLUE"])
                
                if(1):
                    fs = FetchService()
                    ps = PlaylistService()
                    sss = StreamSourceService()
                    sourceId = "03dc9d59-bd52-447f-b373-a35e1453c6f4"
                    playlistId = "1154dd04-cbc8-4fcd-8f8a-ccca0b71dd05"
                    # print(sss.add(StreamSource("Mocked source", "https://www.youtube.com/channel/UCFtc3XdXgLFwhlDajMGK69w", True, 2, True)))
                    # print(ps.add(Playlist("Mocked playlist", [], None, 0, True, True, [sourceId])))
                    print(fs.fetch(playlistId))
                    # print(ps.playCmd(playlistId))
                    
                quit()

            # Print settings
            elif(arg in listSettingsFlags):
                Main.printSettings()

                argIndex += 1
                continue

            elif(arg in listSourcesFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            elif(arg in addSourcesFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            elif(arg in fetchSourceFlags):
                args = extractArgs(argIndex, argV)
                # TODO

                argIndex += len(args) + 1
                continue

            # Invalid, inform and quit
            else:
                printS("Argument not recognized: \"", arg, "\", please see documentation or run with \"-help\" for help.", color=colors["WARNING"])

            argIndex += 1

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

    def printSettings():
        """
        Print settings in .env settings/secrets file.

        Returns:
            None: None
        """

        printS("DEBUG: ", DEBUG,
        "\n", "LOCAL_STORAGE_PATH: ", LOCAL_STORAGE_PATH,
        "\n", "LOG_WATCHED: ", LOG_WATCHED,
        "\n", "DOWNLOAD_WEB_STREAMS: ", DOWNLOAD_WEB_STREAMS,
        "\n", "REMOVE_WATCHED_ON_FETCH: ", REMOVE_WATCHED_ON_FETCH,
        "\n", "PLAYED_ALWAYS_WATCHED: ", PLAYED_ALWAYS_WATCHED,
        "\n", "WATCHED_LOG_FILEPATH: ", WATCHED_LOG_FILEPATH,
        "\n", "BROWSER_BIN: ", BROWSER_BIN)

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
