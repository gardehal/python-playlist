from flask import Flask, render_template
from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.StreamSourceService import StreamSourceService
from Settings import Settings
from enums.StreamSourceType import StreamSourceType

app = Flask(__name__)

settings: Settings = Settings()
playlistService: PlaylistService = PlaylistService()
queueStreamService: QueueStreamService = QueueStreamService()
streamSourceService: StreamSourceService = StreamSourceService()

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

@app.route("/playlists")
def playlistsIndex():
    playlists = playlistService.getAll()
    return render_template("playlists/index.html", playlists= playlists)

@app.route("/playlists/<id>")
def playlistsDetails(id: str):
    playlist = playlistService.get(id)
    queueStreams = playlistService.getStreamsByPlaylistId(id)
    streamSources = playlistService.getSourcesByPlaylistId(id)
    return render_template("playlists/details.html", playlist= playlist, queueStreams= queueStreams, streamSources= streamSources)

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

@app.route("/play/<playlistId>/<int:index>/<watched>")
def play(playlistId: str, index: int, watched: str = "0"):
    playlist = playlistService.get(playlistId)
    queueStream = queueStreamService.get(playlist.streamIds[index])
    
    # TODO better way to pass watched, optional params, also pass video ID if watched, else null, then get and update video watched, not new
    if(eval(watched) and not queueStream.watched): 
        # queueStream.watched = True
        # queueStreamService.update()
        print("DEBUG: queuestream " + queueStream.name + " watched from UI")
        
    # TODO move embedded mapping to service
    embeddedUrl: str = None
    if (queueStream.streamSourceId):
        streamSource = streamSourceService.get(queueStream.streamSourceId)
        if(not streamSource):
            print(f"DEBUG: No streamSource found for queueStream {queueStream.id} {queueStream.name}")
        else:
            if(streamSource.streamSourceTypeId == StreamSourceType.YOUTUBE):
                embeddedUrl = f"https://www.youtube.com/embed/{queueStream.remoteId}?autoplay=1&amp;mute=0&amp;wmode=transparent"
            elif(streamSource.streamSourceTypeId == StreamSourceType.ODYSEE):
                videoIdSplit = queueStream.uri.split("https://odysee.com/")
                embeddedUrl = f"https://odysee.com/$/embed/{videoIdSplit[1]}"
        
    return render_template("play.html", playlist= playlist, queueStream= queueStream, index= index, embeddedUrl= embeddedUrl)

if __name__ == "__main__":
    app.run(host= "0.0.0.0", port= 8888)