# Python Video Queue

Program for queueing and playing videos from list or from sources like YouTube BitChute, Rumble.... 

- Using [MyUtil](https://github.com/grdall/python-packages)
- Using [Python with pip and VS Code](https://github.com/grdall/shared-documentation/blob/main/python-pip-vscode.md)
     
## Installation

1. Download and install Python and PIP
1. Download PIP packages needed for this program to run:
  - ```$ pip install -r path/to/requirements.txt```
1. Create the usable .env-file for setting and secrets:
  - Copy and paste the file .env-example.
  - Rename the file to ".env".
  - Change the values to your liking. The value "BROWSER_BIN" can be left blank. Values which are booleans must be Python parsable, "True", "False", "1", "0" etc.
1. Confirm install by entering the help command:
  - ```$ python main.py -help```
  - Verify that the program prints an overview of commands, arguments, flags, and a description of what they do.

## Help

- All commands can be seen by entering the command "-help".
- Sources currently supported for fetch: YouTube (channels)
- All data is stored locally in human readable JSON files in the path specified in the .env setting LOCAL_STORAGE_PATH. This defaults to "data", in the same folder as the rest of the program. To edit data, it's easier to change these text files directly, as long as you adhere to the JSON format.

## TODO

- play in what? 
  - default video browser for system?
  - Close tab after video is watched not possible? killing selenium too slow, PID from Popen not same PID as browser tab  
  - hidden subprocess for VLC which sets video to watched when video finishes or VLC closes would be nice
- queue videos from channels on youtube since last check
  - Cannot get hours and minutes of video posted? Only day?

- detailed playlist print: add options to not print sources and streams, not to print datetimes, print number of fetched = true sources, and number of watched != None streams
- in detailed print, show streams in order of going to be played chronologically, looks like a diffrence in getall which likely get's by natural sort vs list order added 
- argument to add current playing stream to another playlist (favorites, various playlist for specific topics and music)
- edit parts of object, like playWatchedStreams in Playlist
- confirm delete/remove in commands, delete = soft delete with deleted = datetime field, remove = permanent remove, restore commands - or trashcan instead of hard delete
- some print results, listing sources should list playlist (ID or name), adding/removing anything with relations should specify relation
- adding sources, check for duplicates on url (warning on duplicate name?)
- prune commands for removing watched streams, remove ids from playlists if no corresponding stream, remove sources without playlist?, streams without playlist?
- more detailed use docs?
- tests for core functions like fetch and play?