# Python Video Queue

Program for queueing and playing videos from list or from sources like channels on YouTube, Odysee, Rumble. Data stored locally in JSON files.

- Using [grdUtil](https://github.com/grdall/python-packages)
- Using [Python with pip and VS Code](https://github.com/grdall/shared-documentation/blob/main/python-pip-vscode.md)
     
## Installation

1. Download and install Python and PIP
1. Download [grdUtil](https://github.com/grdall/python-packages), navigate to its base directory and run commands:
    - $ `pip install -r requirements.txt`
    - $ `pip install .`
1. Navigate to the base directory of this project and download PIP packages needed to run:
    - $ `pip install -r requirements.txt`
1. Confirm install by entering the help command:
    - $ `python main.py help` (it is advised you get an alias for "absolute-installation-path/main.py")
    - Verify that the program prints an overview of commands, arguments, flags, and a description of what they do.
    - This will also create the .env file for settings.
1. Optional: Update the file .env with setting and secrets:
    - Change the values to your liking:
      - Values which are booleans must be Python parsable, "True", "False", "1", "0" etc.
      - Paths should be absolute, otherwise they will only work from that relative folder.

## Help

- All commands can be seen by entering the command "help".
- Sources currently supported for fetch: YouTube (channels).
- All data is stored locally in human readable JSON files in the path specified in the .env setting LOCAL_STORAGE_PATH. This defaults to "C:/python/playlists". To edit data, it's easier to change these text files directly, as long as you adhere to the JSON format.
- 2022-04-30: An update in the StreamSource model requires a refactoring of the data.
    - Refactor available under the command `refactor`, eg. $ `python main.py refactor`
    - Example of a changed entity: `... "lastFetchedId": "abc123def", ...` -> `... "lastFetchedIds": ["abc123def"], ...`

## Examples

#### Add a playlist, stream to the playlist, and play it

1. Add a playlist, named "YouTube favourites" which will not play streams already watched and not allow duplicates (of URLs):
    - $ `python main ap "YouTube favourites" False False`
1. See an overview of playlists:
    - $ `python main lp`
    - Will return something like this, where the ID is a randomly generated UUID:
      - `0 - Name: YouTube favourites, ID: 12345678-1234-1234-1234-123456789012, Streams: 0, Sources: 0`
1. Using the index (index + 0 = "i0") from the overview, add [this](https://youtu.be/jNQXAC9IVRw) video from youtube to this playlist:
    - $ `python main a i0 https://youtu.be/jNQXAC9IVRw`
1. Check result in overview of playlists:
    - $ `python main lp`
    - Will return something like this:
      - `0 - Name: YouTube favourites, ID: 12345678-1234-1234-1234-123456789012, Streams: 1, Sources: 0`
1. Play all videos in our playlist:
    - $ `python main p i0`
    - Will return some info for playback:
      - `Playing playlist YouTube feed.`
      - `Starting at stream number: 1, shuffle is off, repeat playlist is off, played videos set to watched is on.`
      - `Now playing "Me at the zoo". This is the last stream, press enter to finish.`
      - `Press enter to play next, "skip" to skip video, or "quit" to quit playback.`
    - Pressing enter would continue the playback and play the next stream, but since this is the last one, pressing enter will finish the playback:
      - `Playlist "YouTube feed" finished.` 
1. Since the option to re-watch streams in playlist is turned off, we can prune our playlist to remove watched streams:
    - $ `python main prune i0`
    - This will bring up a summary:
      - `Prune summary, the following data will be DELETED:`
      - `QueueStream(s)`
      - `abcdefgh-12ab-12ab-12ab-abcdefghijkl - Me at the zoo`
      - ` `
      - `QueueStream ID(s)`
      - `abcdefgh-12ab-12ab-12ab-abcdefghijkl`
      - ` `
      - `(y/n):`
      - `Removing 1 watched QueueStream(s) and 1 IDs in Playlist "YouTube favourites".`
      - `Do you want to DELETE this data?`
      - `(y/n):`
    - Enter "yes" or just "y":
      - `(y/n):yes`
      - `Prune finished, deleted 1 QueueStream(s), 1 ID(s) from Playlist "YouTube favourites".`

#### Add a source to a playlist and fetch streams

1. To our existing playlist, add [this](https://www.youtube.com/c/smartereveryday) YouTube channel and enable fetch:
    - $ `python main as i0 https://www.youtube.com/c/smartereveryday True`
1. Instruct the program to fetch all videos from this channel uploaded after 31st of december, 2021:
    - $ `python main f i0 2021-12-31`
    - This may take some time, depending on the videos available on the channel since given date. Updates will be given when available. This message will be given when finished:
      - `Fetched 3 for playlist "YouTube favourites" successfully.`
1. Check the detailed print of the playlist, here including ALL information available:
    - $ `python main dp i0 True True True True`
1. Or less verbose details, which has most of the information a user needs:
    - $ `python main dp i0`
    - The print would look something like this:
      - `name: YouTube favourites, lastWatchedIndex: 1, playWatchedStreams: False, allowDuplicates: False, description: `
      - `   StreamSources`
      - `   0 - name: SmarterEveryDay - YouTube, isWeb: True, streamSourceTypeId: 2, enableFetch: True`
      - `   `
      - `   QueueStreams`
      - `   1 - name: Video name, isWeb: True`

## TODO

- During playback, adding stream to other playlist, then continuing does not mark stream as watched when it should
- when fetching, if the last fetched stream was deleted, fetch will attempt to fetch all up to batch size..
- play local/directory streams
- support for mp3s
- implement file/folder, Odysee, Rumble fetches
- implement background content properly, should not wait for input, just play when previous stream finished (assume no ads/breaks/pauses, need playtime in model...)
- option to download and watch (requires implement file/folder)
- minor print issues and wording/use of IDs. Some prints can be simplified due to context (e.g. "Added StreamSource "X"", "StreamSource" unnecessary)
- tests for core functions like fetch and play?
- sometimes add source fails due to webrequests/title?
- fetch videos and add in chronologic order, currently adding last video first
- circumvent restrictions using VLC: https://www.electronicshub.org/bypass-youtube-age-restriction/#3_Using_VLC_Media_Player_on_a_Phone_or_Tablet
- fetch youtube still slow, probably still loading all videos from library pytube
- Playback prints can be trimmed