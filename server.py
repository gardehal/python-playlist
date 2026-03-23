import uuid
from queue import Queue
import threading
import sys
import time

from flask import Flask, render_template, request, redirect, url_for, flash, stream_with_context, jsonify, Response
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap5

from grdUtil.DateTimeUtil import getDateTime

from forms.PlaylistForm import *
from forms.QueueStreamForm import *
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
app.secret_key = "foo"# TODO, add to settings
bootstrap = Bootstrap5(app)
activeTasks = {}

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
    if(not playlist):
        flash(f"Playlist {id} was not found.", "error")
        return playlistsIndex()
    
    queueStreams = playlistService.getStreamsByPlaylistId(id)
    streamSources = playlistService.getSourcesByPlaylistId(id)
    enumerateQueueStreams = enumerate(queueStreams) if queueStreams else None
    return render_template("playlists/details.html", playlist= playlist, enumerateQueueStreams= enumerateQueueStreams, streamSources= streamSources)

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
        flash(f"Playlist {id} was not found.", "error")
        return playlistsIndex()
    
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
            
            errorMessage = f"Could not update Playlist id {id}"
        else:
            errorMessage = "Invalid form values"
    
    return render_template("form.html", title= f"Edit {playlist.name}", form= form, errorMessage= errorMessage)

@app.route("/playlists/delete/<id>")
def playlistsDelete(id: str):
    playlist = playlistService.get(id)
    if(not playlist):
        flash(f"Playlist {id} was not found.", "error")
        return playlistsDetails(id)
    
    # TODO alert + accept: f"Delete {playlist.name}?"
    
    deleteResult = playlistService.delete(id)
    if(deleteResult):
        return playlistsIndex()
    else:
        flash(f"Playlist with {id} could not be deleted.", "error")
        return playlistsDetails(id)

@app.route("/queueStreams")
def queueStreamsIndex():
    queueStreams = queueStreamService.getAll()
    return render_template("queueStreams/index.html", queueStreams= queueStreams)

@app.route("/queueStreams/<id>")
def queueStreamsDetails(id: str):
    queueStream = queueStreamService.get(id, True)
    return render_template("queueStreams/details.html", queueStream= queueStream)

@app.route("/queueStreams/create/<playlistId>", methods=["GET", "POST"])
def queueStreamsCreate(playlistId: str):
    playlist = playlistService.get(playlistId)
    if(not playlist):
        flash(f"Playlist {playlistId} was not found.", "error")
        return queueStreamsIndex()
    
    errorMessage = None
    form = QueueStreamForm()
    
    if request.method == "POST":
        if(form.validate_on_submit()):
            queueStream = QueueStream(
                name = form.name.data,
                uri = form.uri.data,
                isWeb = form.isWeb.data,
                streamSourceId = form.streamSourceId.data,
                streamSourceName = form.streamSourceName.data,
                watched = form.watched.data,
                backgroundContent = form.backgroundContent.data,
                playtimeSeconds = form.playtimeSeconds.data,
                remoteId = form.remoteId.data
            )
            
            createResult = queueStreamService.add(queueStream)
            if(createResult):
                playlist.streamIds.append(createResult.id)
                playlistService.update(playlist)
            
            return playlistsDetails(playlistId)
    
    return render_template("form.html", title= "Create new QueueStream", form= form, errorMessage= errorMessage)

@app.route("/queueStreams/edit/<id>", methods=["GET", "POST"])
def queueStreamsEdit(id: str):
    errorMessage = None
    form = QueueStreamForm()
    
    queueStream = queueStreamService.get(id)
    if(not queueStream):
        flash(f"QueueStream with {id} was not found.", "error")
        return queueStreamsIndex()
    
    if request.method == "GET":
        form.name.data = queueStream.name
        form.uri.data = queueStream.uri
        form.isWeb.data = queueStream.isWeb
        form.streamSourceId.data = queueStream.streamSourceId
        form.streamSourceName.data = queueStream.streamSourceName
        form.watched.data = queueStream.watched
        form.backgroundContent.data = queueStream.backgroundContent
        form.playtimeSeconds.data = queueStream.playtimeSeconds
        form.remoteId.data = queueStream.remoteId
    elif request.method == "POST":
        if(form.validate_on_submit()):
            queueStream.name = form.name.data
            queueStream.uri = form.uri.data
            queueStream.isWeb = form.isWeb.data
            queueStream.streamSourceId = form.streamSourceId.data
            queueStream.streamSourceName = form.streamSourceName.data
            queueStream.watched = form.watched.data
            queueStream.backgroundContent = form.backgroundContent.data
            queueStream.playtimeSeconds = form.playtimeSeconds.data
            queueStream.remoteId = form.remoteId.data
            
            updateResult = queueStreamService.update(queueStream)
            
            if(updateResult):
                return queueStreamsDetails(queueStream.id)
                
            errorMessage = f"Could not update QueueStream {id}"
        else:
            errorMessage = "Invalid form values"
    
    return render_template("form.html", title= f"Edit {queueStream.name}", form= form, errorMessage= errorMessage)

@app.route("/queueStreams/delete/<id>")
def queueStreamsDelete(id: str):
    queueStream = queueStreamService.get(id)
    if(not queueStream):
        flash(f"QueueStream {id} was not found.", "error")
        return queueStreamsDetails(id)
    
    flash(f"Delete not implemented until alert confirmation works.", "info")
    return queueStreamsDetails(id)
    
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
    playlist = playlistService.get(playlistId)
    if(not playlist):
        flash(f"Playlist {playlistId} was not found.", "error")
        return streamSourcesIndex()
    
    errorMessage = None
    form = StreamSourceForm()
    
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
        flash(f"StreamSource {id} was not found.", "error")
        return streamSourcesIndex()
    
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
            
            errorMessage = f"Could not update StreamSource {id}"
        else:
            errorMessage = "Invalid form values"
    
    return render_template("form.html", title= f"Edit {streamSource.name}", form= form, errorMessage= errorMessage)

@app.route("/streamSources/delete/<id>")
def streamSourcesDelete(id: str):
    streamSource = streamSourceService.get(id)
    if(not streamSource):
        flash(f"StreamSource {id} was not found.", "error")
        return streamSourcesDetails(id)
    
    flash(f"Delete not implemented until alert confirmation works.", "info")
    return streamSourcesDetails(id)

@app.route("/play/<playlistId>")
def play(playlistId: str):
    playIndex = int(request.args.get("index", 0))
    watchedId = request.args.get("watchedId", None)
    unwatchId = request.args.get("unwatchId", None)
    back = eval(request.args.get("back", "False"))
    
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
        flash(f"Playlist {playlistId} was not found.", "error")
        return index()
    if(playIndex < 0 or playIndex >= len(playlist.streamIds)):
        flash(f"Index was out of range of playlist {playlist.name}, max index: {len(playlist.streamIds) - 1}", "error")
        return playlistsDetails(id = playlist.id)
    
    queueStreamId = playlist.streamIds[playIndex]
    queueStream = queueStreamService.get(queueStreamId)
    if(not queueStream):
        flash(f"QueueStream {queueStreamId}, index {playIndex} was not found.", "error")
        return playlistsDetails(id = playlist.id)
    
    if(not back and queueStream.watched and not playlist.playWatchedStreams):
        return redirect(url_for("play", playlistId= playlistId, index= playIndex+1))
    
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
    
    nextQueueStreams = []
    for nextQueueStreamId in playlist.streamIds[playIndex+1:][:4]: # Next 4, if any
        nextQueueStream = queueStreamService.get(nextQueueStreamId)
        if(nextQueueStream):
            nextQueueStreams.append(nextQueueStream)
        
    enumeratedNextQueueStreams = enumerate(nextQueueStreams, playIndex) if nextQueueStreams else None
    return render_template("play.html", playlist= playlist, queueStream= queueStream, index= playIndex, 
        embeddedUrl= embeddedUrl, circumventUrl= circumventUrl, fileUri= fileUri, 
        enumeratedNextQueueStreams= enumeratedNextQueueStreams)

@app.route("/fetch/<playlistId>")
def fetchPlaylist(playlistId):
    playlist = playlistService.get(playlistId)
    
    started = getDateTime()
    newQueueStreams = fetchService.fetch(playlist.id, settings.fetchLimitSingleSource, takeNewOnly= True)
    duration = getDateTime() - started # ToHumanReadableString()
    
    return render_template("fetch.html", playlist= playlist, newQueueStreams= newQueueStreams, duration= duration)

@app.route("/prune/<playlistId>")
def prunePlaylist(playlistId):
    playlist = playlistService.get(playlistId)
    
    data = sharedService.preparePrune(playlistId)
    pruneResult = sharedService.doPrune(data)
    if(pruneResult):
        # TODO len here is soft deleted, not actually removed ones, gives "wrong" result
        flash(f"Pruned {len(data.queueStreams)} QueueStreams in Playlist {playlist.name}", "success")
    
    return playlistsDetails(playlistId)

@app.route("/purge")
def purgeAll():
    data = sharedService.preparePurge()
    
    # print results and ask for confirmation
    
    if(False):
        result = self.sharedService.doPurge(data)
        if(result):
            printS("Purge completed.", color = BashColor.OKGREEN)
        else:
            printS("Purge failed.", color = BashColor.FAIL)
    
    flash(f"Not implemented.", "info")
    return index()

@app.route("/softDeleted")
def softDeletedIndex():
    playlists = [e for e in playlistService.getAll(True) if e.deleted]
    queueStreams = [e for e in queueStreamService.getAll(True) if e.deleted]
    streamSources = [e for e in streamSourceService.getAll(True) if e.deleted]
    
    return render_template("softDeleted.html", playlists= playlists, queueStreams= queueStreams, streamSources= streamSources)

@csrf.exempt
@app.route("/enqueueTask", methods=["POST"])
def start_task():
    input_data = request.get_json() or {}

    jobId = str(uuid.uuid4())
    logQueue = Queue()
    activeTasks[jobId] = logQueue

    def run_task():
        custom_stream = StreamToQueue(logQueue)
        old_stdout = sys.stdout
        sys.stdout = custom_stream

        try:
            print("Starting processing...")
            print("Step 1 completed")
            
            time.sleep(5)
            print("halfway")
            time.sleep(5)
                        
            print("Task finished successfully!")

        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            sys.stdout = old_stdout
            logQueue.put(None)

    threading.Thread(target= run_task, daemon= True).start()

    return jsonify({"jobId": jobId})

@csrf.exempt
@app.route("/streamLogs")
def streamLogs():
    jobId = request.args.get("jobId")
    if not jobId or jobId not in activeTasks:
        return "Job not found", 404

    def generate():
        q = activeTasks[jobId]
        while True:
            line = q.get()
            if line is None:
                del activeTasks[jobId]
                yield "data: [DONE]\n\n"
                break
            yield f"data: {line}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})

class StreamToQueue:
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        if text:
            self.queue.put(text.rstrip())
            
    def flush(self):
        pass
    
if __name__ == "__main__":
    # print("Routes:")
    # for rule in app.url_map.iter_rules():
    #     print(f"{rule.rule} - {rule.methods} - {rule.endpoint}")
    
    app.run(host= "0.0.0.0", port= 8888)