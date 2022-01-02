# Python Video Queue

Program for queueing and playing videos from list or from sources like YouTube BitChute, Rumble.... 

- Using [MyUtil](https://github.com/grdall/python-packages)
- Using [Python with pip and VS Code](https://github.com/grdall/shared-documentation/blob/main/python-pip-vscode.md)

## TODO

- play in what? 
  - default video browser for system?
  - Close tab after video is watched not possible? killing selenium too slow, PID from Popen not same PID as browser tab  
  - hidden subprocess for VLC which sets video to watched when video finishes or VLC closes would be nice
- queue videos from channels on youtube since last check
  - Cannot get hours and minutes of video posted? Only day?

- setup CLI for everything
  - update help-print
  - Better way to deal with input and types, e.g. eval("false") fails, named input like --mylist = 1, 2, 3?
  - easier way to deal with the uid IDs? any possibility of making them tabable or shorter with guaranteed unique?
- prune commands for removing watched streams, remove ids from playlists if no corresponding stream, remove sources without playlist?, streams without playlist?
- more detailed use docs?
- tests for core functions like fetch and play?