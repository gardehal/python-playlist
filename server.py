from flask import Flask, render_template, request
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap5

from forms.PlaylistForm import *

from Settings import Settings
from services.PlaylistService import *
from services.QueueStreamService import *
from services.StreamSourceService import *
from services.PlaybackService import *
from services.FetchService import *
from services.SharedService import *

app = Flask(__name__)
csrf = CSRFProtect(app)
# TODO, add to settings
app.secret_key = "foo"
bootstrap = Bootstrap5(app)

settings = Settings()
playlistService = PlaylistService()
queueStreamService = QueueStreamService()
streamSourceService = StreamSourceService()
playbackService = PlaybackService()
fetchService = FetchService()
sharedService = SharedService()

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", defaultPlaylistId= settings.defaultPlaylistId)

@app.route("/help")
@app.route("/docs")
def help():
    return render_template("help.html")

@app.route("/quit")
def quitApp():
    quit() # not working? should end server/program locally
    return index()

@app.route("/error")
def error():
    errorMessage = request.args.get("errorMessage", "An unspecified error has occurred! Please check the logs for details.")
    return render_template("error.html", errorMessage= errorMessage)

@app.route("/playlists")
def playlistsIndex():
    playlists = playlistService.getAllSorted()
    return render_template("playlists/index.html", playlists= playlists)

@app.route("/playlists/<id>")
def playlistsDetails(id: str):
    playlist = playlistService.get(id)
    queueStreams = playlistService.getStreamsByPlaylistId(id)
    streamSources = playlistService.getSourcesByPlaylistId(id)
    return render_template("playlists/details.html", playlist= playlist, enumerateQueueStreams= enumerate(queueStreams), streamSources= streamSources)

@app.route("/playlists/create", methods=["GET", "POST"])
def playlistsCreate():
    form = PlaylistForm()
    errorMessage = None
    
    if(form.validate_on_submit()):
        playlist = Playlist(
            name = form.name.data,
            playWatchedStreams = form.playWatchedStreams.data,
            allowDuplicates = form.allowDuplicates.data,
            description = form.description.data,
            favorite = form.favorite.data,
            sortOrder = form.sortOrder.data,
            lastWatchedIndex = 0,
            streamSourceIds = [],
            streamIds = [],
        )
        
        playlistService.add(playlist)
        return playlistsDetails(playlist.id)
    # else:
    #     errorMessage = "Fields were not valid"
    
    return render_template("form.html", title= "Create new Playlist", form= form, errorMessage= errorMessage)

@app.route("/playlists/delete/<id>")
def playlistsDelete(id: str):
    playlist = playlistService.get(id)
    if(playlist):
        # TODO alert: f"Delete {playlist.name}"?
        
        deleteResult = playlistService.delete(id)
        if(deleteResult):
            return playlistsIndex()
        else:
            return error(f"Playlist with {id} could not be deleted.")
    else:
        return error(f"Playlist with {id} does not exist.")

@app.route("/queueStreams")
def queueStreamsIndex():
    queueStreams = queueStreamService.getAll()
    return render_template("queueStreams/index.html", queueStreams= queueStreams)

@app.route("/queueStreams/<id>")
def queueStreamsDetails(id: str):
    queueStream = queueStreamService.get(id)
    return render_template("queueStreams/details.html", queueStream= queueStream)

@app.route("/streamSources")
def streamSourcesIndex():
    streamSources = streamSourceService.getAll()
    return render_template("streamSources/index.html", streamSources= streamSources)

@app.route("/streamSources/<id>")
def streamSourcesDetails(id: str):
    streamSource = streamSourceService.get(id)
    return render_template("streamSources/details.html", streamSource= streamSource)

@app.route("/play/<playlistId>")
def play(playlistId: str):
    index = int(request.args.get("index", 0))
    watchedId = request.args.get("watchedId", None)
 
    playlist = playlistService.get(playlistId)
    queueStream = queueStreamService.get(playlist.streamIds[index])
    
    if(watchedId): 
        watchedQueueStream = queueStreamService.get(watchedId)
        if(watchedQueueStream):
            watchedQueueStream.watched = True
            queueStreamService.update(watchedQueueStream)
            print("DEBUG: QueueStream " + watchedQueueStream.name + " watched from UI")
        
    if(index < 0 or index >= len(playlist.streamIds)):
        return error(f"Index was out of range of playlist {playlist.name}, max index: {len(playlist.streamIds) - 1}")
    
    embeddedUrl: str = None
    if (queueStream.streamSourceId):
        embeddedUrl = playbackService.mapUrlToEmbeddedUrl(queueStream)
        
    circumventUrl = playbackService.getRestrictCircumventedUrl(queueStream)
        
    return render_template("play.html", playlist= playlist, queueStream= queueStream, index= index, embeddedUrl= embeddedUrl, circumventUrl= circumventUrl)

@app.route("/fetch/<playlistId>")
def fetchPlaylist(playlistId):
    playlist = playlistService.get(playlistId)
    
    # TODO while fetching, show some spinner + prints in fetching.html or something
    newQueueStreams = fetchService.fetch(playlist.id, settings.fetchLimitSingleSource, takeNewOnly= True)
    
    return render_template("fetch.html", playlist= playlist, newQueueStreams= newQueueStreams)

@app.route("/prune/<playlistId>")
def prunePlaylist(playlistId):
    playlist = playlistService.get(playlistId)
    
    data = sharedService.preparePrune(playlistId)
    pruneResult = sharedService.doPrune(data)
    if(pruneResult):
        # TODO get flask-modals or something and add toast with result
        print(f"Pruned {len(data.queueStreams)} QueueStreams in Playlist {playlist.name}")
    
    return playlistsDetails(playlistId)

if __name__ == "__main__":
    app.run(host= "0.0.0.0", port= 8888)