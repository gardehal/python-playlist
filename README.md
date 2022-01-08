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

## TODO

- play in what? 
  - default video browser for system?
  - Close tab after video is watched not possible? killing selenium too slow, PID from Popen not same PID as browser tab  
  - hidden subprocess for VLC which sets video to watched when video finishes or VLC closes would be nice
- queue videos from channels on youtube since last check
  - Cannot get hours and minutes of video posted? Only day?

- pytube titles and page titles sanitization, error whe title has special univode like \u1234 or ' etc
- reset fetch command, removes all streams in playlist, sets related sources lastfetch to None
- confirm delete/remove in commands, delete = soft delete, remove = permanent remove, restore commands
- some print results, listing sources should list playlist (ID or name), adding/removing anything with relations should specify relation
- adding sources, check for duplicates on url (warning on duplicate name?)
- prune commands for removing watched streams, remove ids from playlists if no corresponding stream, remove sources without playlist?, streams without playlist?
- more detailed use docs?
- tests for core functions like fetch and play?