from flask import Flask, render_template
from services.PlaylistService import PlaylistService

app = Flask(__name__)

playlistService: PlaylistService = PlaylistService()
# https://www.youtube.com/watch?v=jQjjqEjZK58
    
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/help")
@app.route("/docs")
def help():
    return render_template("help.html")

@app.route("/playlists")
def playlistIndex():
    playlists = playlistService.getAll()
    return render_template("playlists/index.html", playlists= playlists)

@app.route("/playlists/1")
def playlistDetails():
    return render_template("playlists/details.html")

@app.route("/sources")
@app.route("/streamsources")
def sourcesIndex():
    return render_template("streamsources/index.html")

@app.route("/streamsources/1")
def sourcesDetails():
    return render_template("streamsources/details.html")

@app.route("/steams")
@app.route("/queuestreams")
def streamIndex():
    return render_template("streamsources/index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)