from io import StringIO
import os
import sys
import json
from model.VideoSource import VideoSource
from myutil.Util import *
from myutil.DateTimeObject import *
from pytube import YouTube
from dotenv import load_dotenv

load_dotenv()
debug = False
settingsFilename = "settings.json"
sourcesFilename = "queuesources.json"
queueFilename = "queue.txt"

os.system("") # Needed to "trigger" coloured text
helpFlags = ["-help", "-h"]
testFlags = ["-test", "-t"]
playFlags = ["-play", "-p"]
listQueueFlags = ["-list", "-l"]
addVideoFlags = ["-add", "-a"]
removeVideoFlags = ["-remove", "-rm", "-r"]
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

                quit()

            elif(arg in addSourcesFlags):
                args = extractArgs(argIndex, argV)
                
                sourcesAdded = Main.addSource(args)
                if(sourcesAdded != None and sourcesAdded > 0):
                    printS("Added ", sourcesAdded, " new sources", color=colors["OKGREEN"])
                    continue

                argIndex += len(args) + 1
                continue

            # Invalid, inform and quit
            else:
                printS("Argument not recognized: \"", arg, "\", please see documentation or run with \"-help\" for help.", color=colors["WARNING"])

            argIndex += 1
            
    def createLocalFilesIfNone() -> bool:
        """"
        Create local files used for storing settings, video ques, sources etc.
        \nreturns success = true
        """
        
        files = [settingsFilename, sourcesFilename, queueFilename]
        
        for file in files:
            open(file, "a")
            
        return True
    
    def toDict(obj: object) -> dict:
        """ 
        Converts objects to dictionaries.
        \nSource: https://www.codegrepper.com/code-examples/whatever/python+nested+object+to+dict
        \nreturn a dictionary of input object
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
        \nreturns JSON string
        """
        dict = Main.toDict(obj)
        return json.dumps(dict, default=str)
            
    def addSource(sources) -> int:
        """
        Add video source(s) to list of watched sources.
        \nreturns number of added sources
        """
        
        fileContent = open(sourcesFilename, "r").read()
        fileSources = json.loads(fileContent if len(fileContent) > 0 else """{"sources":[]}""")
        updatedSourcesJson = fileSources
        
        addedSources = 0
        for source in sources:
            isUrl = validators.url(source)
            url = source if isUrl else None
            dir = source if os.path.exists(source) else None
            if(url == None and dir == None):
                printS("The source: ", source, "is not a valid URL or directory path.", color=colors["ERROR"])
                continue
            
            addedSources += 1
            dto = DateTimeObject()
            newSource = VideoSource("name", url, dir, isUrl, True, dto, dto)
            updatedSourcesJson["sources"].append(Main.toDict(newSource))
            
        f = open(sourcesFilename, "w") # Truncate
        j = json.dumps(Main.toJson(updatedSourcesJson))
        print(j)
        f.writelines(j)
        f.close
        
        return addedSources 

    def printHelp():
        """
        A simple console print that informs user of program arguments.
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
        printS(addSourcesFlags, " + [1+ URLs or paths to directories]: Adds a video source to list of watched sources.")
        printS(removeSourceFlags, " + [1+ URLs or paths to directories]: Removes video source(s) from list of watched sources.")
        printS(fetchSourceFlags, ": Update queue with videos from list of watched sources.")
        
if __name__ == "__main__":
    Main.main()