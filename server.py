from flask import Flask, render_template, request
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap5

from grdUtil.DateTimeUtil import getDateTime

from forms.PlaylistForm import *
from forms.StreamSourceForm import *

from Settings import *
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
    return renderError(errorMessage)

def renderError(errorMessage: str):
    return render_template("error.html", errorMessage= errorMessage)

@app.route("/playlists")
def playlistsIndex():
    playlists = playlistService.getAllSorted()
    return render_template("playlists/index.html", playlists= playlists)

@app.route("/playlists/<id>")
def playlistsDetails(id: str):
    playlist = playlistService.get(id, True)
    queueStreams = playlistService.getStreamsByPlaylistId(id)
    streamSources = playlistService.getSourcesByPlaylistId(id)
    return render_template("playlists/details.html", playlist= playlist, enumerateQueueStreams= enumerate(queueStreams), streamSources= streamSources)

@app.route("/playlists/create", methods=["GET", "POST"])
def playlistsCreate():
    errorMessage = None
    form = PlaylistForm()
    
    if request.method == "POST":
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
    
    return render_template("form.html", title= "Create new Playlist", form= form, errorMessage= errorMessage)

@app.route("/playlists/edit/<id>", methods=["GET", "POST"])
def playlistsEdit(id: str):
    errorMessage = None
    form = PlaylistForm()
    
    playlist = playlistService.get(id)
    if(not playlist):
        return renderError(f"No Playlist found for id {id}")
    else:
        if request.method == "GET":
            form.name.data = playlist.name
            form.playWatchedStreams.data = playlist.playWatchedStreams
            form.allowDuplicates.data = playlist.allowDuplicates
            form.description.data = playlist.description
            form.favorite.data = playlist.favorite
            form.sortOrder.data = playlist.sortOrder
        elif request.method == "POST":
            if(form.validate_on_submit()):
                playlist.name = form.name.data
                playlist.playWatchedStreams = form.playWatchedStreams.data
                playlist.allowDuplicates = form.allowDuplicates.data
                playlist.description = form.description.data
                playlist.favorite = form.favorite.data
                playlist.sortOrder = form.sortOrder.data
                
                updateResult = playlistService.update(playlist)
                
                if(updateResult):
                    return playlistsDetails(playlist.id)
                else:
                    errorMessage = f"Could not update Playlist id {id}"
            else:
                errorMessage = "Invalid form values"
    
    return render_template("form.html", title= f"Edit {playlist.name}", form= form, errorMessage= errorMessage)

@app.route("/playlists/delete/<id>")
def playlistsDelete(id: str):
    playlist = playlistService.get(id)
    if(playlist):
        # TODO alert + accept: f"Delete {playlist.name}?"
        
        deleteResult = playlistService.delete(id)
        if(deleteResult):
            return playlistsIndex()
        else:
            return renderError(f"Playlist with {id} could not be deleted.")
    else:
        return renderError(f"Playlist {id} was not found.")

@app.route("/queueStreams")
def queueStreamsIndex():
    queueStreams = queueStreamService.getAll()
    return render_template("queueStreams/index.html", queueStreams= queueStreams)

@app.route("/queueStreams/<id>")
def queueStreamsDetails(id: str):
    queueStream = queueStreamService.get(id, True)
    return render_template("queueStreams/details.html", queueStream= queueStream)

@app.route("/streamSources")
def streamSourcesIndex():
    streamSources = streamSourceService.getAll()
    return render_template("streamSources/index.html", streamSources= streamSources)

@app.route("/streamSources/<id>")
def streamSourcesDetails(id: str):
    streamSource = streamSourceService.get(id, True)
    return render_template("streamSources/details.html", streamSource= streamSource)

@app.route("/streamSources/create/<playlistId>", methods=["GET", "POST"])
def streamSourcesCreate(playlistId: str):
    errorMessage = None
    form = StreamSourceForm()
    
    playlist = playlistService.get(playlistId)
    if(not playlist):
        return renderError(f"Playlist {playlistId} was not found.")
    
    if request.method == "POST":
        if(form.validate_on_submit()):
            streamSource = StreamSource(
                name = form.name.data,
                uri = form.uri.data,
                isWeb = form.isWeb.data,
                enableFetch = form.enableFetch.data,
                backgroundContent = form.backgroundContent.data,
                alwaysDownload = form.alwaysDownload.data,
                streamSourceTypeId = 0,
                lastSuccessfulFetched = None,
                lastFetchedIds = [],
                lastFetched = None
            )
            
            createResult = streamSourceService.add(streamSource)
            if(createResult):
                playlist.streamSourceIds.append(createResult.id)
                playlistService.update(playlist)
            
                return playlistsDetails(playlistId)
    
    return render_template("form.html", title= "Create new StreamSource", form= form, errorMessage= errorMessage)

@app.route("/streamSources/edit/<id>", methods=["GET", "POST"])
def streamSourcesEdit(id: str):
    errorMessage = None
    form = StreamSourceForm()
    
    streamSource = streamSourceService.get(id)
    if(not streamSource):
        return renderError(f"StreamSource {id} was not found.")
    else:
        if request.method == "GET":
            form.name.data = streamSource.name
            form.uri.data = streamSource.uri
            form.streamSourceTypeId.data = streamSource.streamSourceTypeId
            form.isWeb.data = streamSource.isWeb
            form.enableFetch.data = streamSource.enableFetch
            form.backgroundContent.data = streamSource.backgroundContent
            form.alwaysDownload.data = streamSource.alwaysDownload
        elif request.method == "POST":
            if(form.validate_on_submit()):
                streamSource.name = form.name.data
                streamSource.uri = form.uri.data
                streamSource.streamSourceTypeId = form.streamSourceTypeId.data
                streamSource.isWeb = form.isWeb.data
                streamSource.enableFetch = form.enableFetch.data
                streamSource.backgroundContent = form.backgroundContent.data
                streamSource.alwaysDownload = form.alwaysDownload.data
                
                updateResult = streamSourceService.update(streamSource)
                
                if(updateResult):
                    return streamSourcesDetails(streamSource.id)
                else:
                    errorMessage = f"Could not update StreamSource {id}"
            else:
                errorMessage = "Invalid form values"
    
    return render_template("form.html", title= f"Edit {streamSource.name}", form= form, errorMessage= errorMessage)

@app.route("/play/<playlistId>")
def play(playlistId: str):
    index = int(request.args.get("index", 0))
    watchedId = request.args.get("watchedId", None)
    unwatchId = request.args.get("unwatchId", None)
    
    # Move somewhere else, serverhelper.py or something
    if(watchedId): 
        watchedQueueStream = queueStreamService.get(watchedId)
        if(watchedQueueStream):
            watchedQueueStream.watched = getDateTime()
            queueStreamService.update(watchedQueueStream)
            print("DEBUG: QueueStream " + watchedQueueStream.name + " watched from UI")
            
    if(unwatchId): 
        unwatchedQueueStream = queueStreamService.get(unwatchId)
        if(unwatchedQueueStream):
            unwatchedQueueStream.watched = None
            queueStreamService.update(unwatchedQueueStream)
            print("DEBUG: QueueStream " + unwatchedQueueStream.name + " unwatch from UI")
        
    playlist = playlistService.get(playlistId)
    if(not playlist):
        return renderError(f"Playlist {playlistId} was not found.")
    if(index < 0 or index >= len(playlist.streamIds)):
        return renderError(f"Index was out of range of playlist {playlist.name}, max index: {len(playlist.streamIds) - 1}")
    
    queueStreamId = playlist.streamIds[index]
    queueStream = queueStreamService.get(queueStreamId)
    if(not queueStream):
        return renderError(f"QueueStream {queueStreamId} was not found.")
    
    embeddedUrl: str = None
    circumventUrl: str = None
    fileUri: str = None
    if(queueStream.isWeb):
        if (queueStream.streamSourceId):
            embeddedUrl = playbackService.mapUrlToEmbeddedUrl(queueStream)
            
        circumventUrl = playbackService.getRestrictCircumventedUrl(queueStream)
    else:
        # Abs paths dont work, copy file over?
        # fast api symlink wont work without replacing entire flask
        fileUri = playbackService.mapUrlToEmbeddedUrl(queueStream)
    
    # TODO fix index when clicking these, dict index + qs?, fix formating, text overlay over image, fix size too
    nextQueueStreams = []
    for nextQueueStreamId in playlist.streamIds[index+1:][:4]: # Next 4, if any
        nextQueueStream = queueStreamService.get(nextQueueStreamId)
        if(nextQueueStream):
            nextQueueStreams.append(nextQueueStream)
        
    return render_template("play.html", playlist= playlist, queueStream= queueStream, index= index, 
                           embeddedUrl= embeddedUrl, circumventUrl= circumventUrl, fileUri= fileUri, 
                           nextQueueStreams= nextQueueStreams)

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

@app.route("/softDeleted")
def softDeletedIndex():
    playlists = [e for e in playlistService.getAll(True) if e.deleted]
    queueStreams = [e for e in queueStreamService.getAll(True) if e.deleted]
    streamSources = [e for e in streamSourceService.getAll(True) if e.deleted]
    
    return render_template("softDeleted.html", playlists= playlists, queueStreams= queueStreams, streamSources= streamSources)

if __name__ == "__main__":
    app.run(host= "0.0.0.0", port= 8888)