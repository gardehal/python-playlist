import re
import os
import sys
from myutil.Util import *
from myutil.DateTimeObject import *
from pytube import YouTube
from dotenv import load_dotenv
load_dotenv()
debug = False

os.system("") # Needed to "trigger" coloured text
helpFlags = ["-help", "-h"]
testFlags = ["-test", "-t"]
downloadFlags = ["-download", "-d"]
editSpliceSwitches = ["splice", "spl", "join", "j"]

youTubeFlags = ["-youtube", "-yt"]

class Main:
    def main():
        argC = len(sys.argv)
        argV = sys.argv
        argIndex = 1

        if(argC < 2):
            Main.printHelp()

        while argIndex < argC:
            arg = sys.argv[argIndex].lower()

            if(arg in helpFlags):
                Main.printHelp()

            elif(arg in testFlags):
                args = extractArgs(argIndex, argV)
                print("test")

                quit()

            elif(arg in downloadFlags):
                args = extractArgs(argIndex, argV)

                argIndex += len(args) + 1
                continue

            # Invalid, inform and quit
            else:
                printS("Argument not recognized: \"", arg, "\", please see documentation or run with \"-help\" for help.", color=colors["WARNING"])

            argIndex += 1

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

        printS(downloadFlags, " + [URL]: Downloads a file from the URL argument.")
        printS("\t", editSpliceSwitches, " + [filepaths to splice]: Splice/join two or more videos or audio files after each other, in given order.")
        
if __name__ == "__main__":
    Main.main()