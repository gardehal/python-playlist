from flask import Flask, render_template, request

from Settings import Settings

from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.StreamSourceService import StreamSourceService
from services.PlaybackService import PlaybackService
from services.FetchService import FetchService

app = Flask(__name__)

settings: Settings = Settings()
playlistService: PlaylistService = PlaylistService()
queueStreamService: QueueStreamService = QueueStreamService()
streamSourceService: StreamSourceService = StreamSourceService()
playbackService: PlaybackService = PlaybackService()
fetchService: FetchService = FetchService()

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
    quit() # ?
    return

@app.route("/error")
def error(errorMessage: str):
    return render_template("error.html", errorMessage= errorMessage)

@app.route("/playlists")
def playlistsIndex():
    playlists = playlistService.getAll()
    return render_template("playlists/index.html", playlists= playlists)

@app.route("/playlists/<id>")
def playlistsDetails(id: str):
    playlist = playlistService.get(id)
    queueStreams = playlistService.getStreamsByPlaylistId(id)
    streamSources = playlistService.getSourcesByPlaylistId(id)
    return render_template("playlists/details.html", playlist= playlist, enumerateQueueStreams= enumerate(queueStreams), streamSources= streamSources)

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

if __name__ == "__main__":
    app.run(host= "0.0.0.0", port= 8888)