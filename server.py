from flask import Flask, render_template
from services.PlaylistService import PlaylistService
from services.QueueStreamService import QueueStreamService
from services.StreamSourceService import StreamSourceService

app = Flask(__name__)

playlistService: PlaylistService = PlaylistService()
queueStreamService: QueueStreamService = QueueStreamService()
streamSourceService: StreamSourceService = StreamSourceService()

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

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

@app.route("/play/<playlistId>/<index>")
def play(playlistId: str, index: int):
    # TODO
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)