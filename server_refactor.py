import uuid
from queue import Queue
import threading
import sys
import time

from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, stream_with_context, jsonify, Response
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap5

from grdUtil.DateTimeUtil import getDateTime

from forms.PlaylistForm import *
from forms.QueueStreamForm import *
from forms.StreamSourceForm import *
from forms.YoutubePlaylistForm import *

from Settings import *
from datetime import datetime
from application.use_cases.add_stream_to_playlist_use_case import AddStreamToPlaylistUseCase
from application.use_cases.create_playlist_from_youtube_use_case import CreatePlaylistFromYoutubeUseCase
from application.use_cases.create_playlist_use_case import CreatePlaylistUseCase
from application.use_cases.create_queue_stream_use_case import CreateQueueStreamUseCase
from application.use_cases.create_stream_source_use_case import CreateStreamSourceUseCase
from application.use_cases.delete_playlist_use_case import DeletePlaylistUseCase
from application.use_cases.delete_queue_stream_use_case import DeleteQueueStreamUseCase
from application.use_cases.delete_stream_source_use_case import DeleteStreamSourceUseCase
from application.use_cases.get_all_playlists_use_case import GetAllPlaylistsUseCase
from application.use_cases.get_all_queue_streams_use_case import GetAllQueueStreamsUseCase
from application.use_cases.get_playlist_details_use_case import GetPlaylistDetailsUseCase
from application.use_cases.get_queue_stream_details_use_case import GetQueueStreamDetailsUseCase
from application.use_cases.get_stream_source_details_use_case import GetStreamSourceDetailsUseCase
from application.use_cases.toggle_queue_stream_watched_use_case import ToggleQueueStreamWatchedUseCase
from application.use_cases.update_playlist_use_case import UpdatePlaylistUseCase
from application.use_cases.update_queue_stream_use_case import UpdateQueueStreamUseCase
from application.use_cases.update_stream_source_use_case import UpdateStreamSourceUseCase
from infrastructure.repositories.base_service_playlist_repository import BaseServicePlaylistRepository, PlaylistRepository
from infrastructure.repositories.base_service_queue_stream_repository import QueueStreamRepository
from infrastructure.repositories.base_service_stream_source_repository import StreamSourceRepository
from infrastructure.providers.youtube_provider import YoutubeProvider

app = Flask(__name__)
csrf = CSRFProtect(app) 
app.secret_key = "foo"# TODO, add to settings
bootstrap = Bootstrap5(app)
activeTasks = {}
taskRegistry = {}

playlistRepository = BaseServicePlaylistRepository()
queueStreamRepository = QueueStreamRepository(playlistRepository)
streamSourceRepository = StreamSourceRepository(playlistRepository)

getAllPlaylistsUseCase = GetAllPlaylistsUseCase(playlistRepository)
getAllQueueStreamsUseCase = GetAllQueueStreamsUseCase(queueStreamRepository)
getAllStreamSourcesUseCase = GetAllStreamSourcesUseCase(streamSourceRepository)
createPlaylistUseCase = CreatePlaylistUseCase(playlistRepository)
createPlaylistFromYoutubeUseCase = CreatePlaylistFromYoutubeUseCase(
    playlist_repository=playlistRepository, 
    queue_stream_repository=queueStreamRepository
)
getPlaylistDetailsUseCase = GetPlaylistDetailsUseCase(
    playlist_repository=playlistRepository,
    queue_stream_repository=queueStreamRepository,
    stream_source_repository=streamSourceRepository
)
getQueueStreamDetailsUseCase = GetQueueStreamDetailsUseCase(queueStreamRepository)
updatePlaylistUseCase = UpdatePlaylistUseCase(playlistRepository)
updateQueueStreamUseCase = UpdateQueueStreamUseCase(queueStreamRepository)
deletePlaylistUseCase = DeletePlaylistUseCase(playlistRepository)
deleteQueueStreamUseCase = DeleteQueueStreamUseCase(queueStreamRepository)
createQueueStreamUseCase = CreateQueueStreamUseCase(playlistRepository, queueStreamRepository)
createStreamSourceUseCase = CreateStreamSourceUseCase(playlistRepository, streamSourceRepository)
updateStreamSourceUseCase = UpdateStreamSourceUseCase(streamSourceRepository)
deleteStreamSourceUseCase = DeleteStreamSourceUseCase(streamSourceRepository)
toggleWatchedUseCase = ToggleQueueStreamWatchedUseCase(queueStreamRepository)
addStreamToPlaylistUseCase = AddStreamToPlaylistUseCase(playlistRepository, queueStreamRepository)
getStreamSourceDetailsUseCase = GetStreamSourceDetailsUseCase(streamSourceRepository)

def registerTask(name):
    def decorator(func):
        taskRegistry[name] = func
        return func
    return decorator

def reloadPage():
    return redirect(request.referrer or url_for("index"))

@app.route("/")
@app.route("/index")
def index():
    default_id = settings.defaultPlaylistId
    is_default_valid = bool(default_id and playlistService.get(default_id))
    return render_template("index.html", defaultPlaylistId=settings.defaultPlaylistId, isDefaultValid=is_default_valid)

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

@app.route("/playlists/from-youtube", methods=["GET", "POST"])
def playlistsFromYoutube():
    errorMessage = None
    form = YoutubePlaylistForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            playlistId = createPlaylistFromYoutubeUseCase.execute(
                url=form.url.data,
                name=form.name.data or None,
                description=form.description.data or None,
                play_watched_streams=form.playWatchedStreams.data,
                allow_duplicates=form.allowDuplicates.data,
                favorite=form.favorite.data,
                sort_order=form.sortOrder.data
            ).id # Assuming the use case returns the playlist with its new ID
            
            flash(f"Created playlist from YouTube URL", "success")

            return playlistsDetails(playlistId)
        except Exception as e:
            flash(f"Error creating playlist: {str(e)}", "error")
    
    return render_template("form.html", title="Create new Playlist from YouTube", form=form, errorMessage=errorMessage)

@app.route("/playlists")
def playlistsIndex():
    playlists = getAllPlaylistsUseCase.execute()
    return render_template("playlists/index.html", playlists= playlists)

@app.route("/playlists/<id>")
def playlistsDetails(id: str):
    detailsDto = getPlaylistDetailsUseCase.execute(id)
    if not detailsDto:
        flash(f"Playlist {id} was not found.", "error")
        return playlistsIndex()
    
    playlist = detailsDto.playlist
    queueStreams = detailsDto.queue_streams
    streamSources = detailsDto.stream_sources
    enumerateQueueStreams = enumerate(queueStreams) if queueStreams else None
    return render_template("playlists/details.html", playlist=playlist, enumerateQueueStreams=enumerateQueueStreams, streamSources=streamSources)

@app.route("/playlist/<playlistId>/toggle_watched/<streamId>", methods=["POST"])
def toggleWatched(playlistId: str, streamId: str):
    try:
        toggleWatchedUseCase.execute(streamId)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route("/playlists/create", methods=["GET", "POST"])
def playlistsCreate():
    errorMessage = None
    form = PlaylistForm()
    
    if request.method == "POST" and form.validate_on_submit():
        try:
            playlist = createPlaylistUseCase.execute(
                name=form.name.data,
                description=form.description.data or None,
                play_watched_streams=form.playWatchedStreams.data,
                allow_duplicates=form.allowDuplicates.data,
                favorite=form.favorite.data,
                sort_order=form.sortOrder.data
            )
            flash(f"Created playlist: {playlist.name}", "success")
            return redirect(url_for("playlistsIndex"))
        except Exception as e:
            flash(f"Error creating playlist: {str(e)}", "error")
    
    return render_template("form.html", title="Create new Playlist", form=form, errorMessage=errorMessage)


@app.route("/playlists/edit/<id>", methods=["GET", "POST"])
def playlistsEdit(id: str):
    errorMessage = None
    form = PlaylistForm()
    
    try:
        playlist = playlistRepository.get_by_id(id)
        if not playlist:
            flash(f"Playlist {id} was not found.", "error")
            return playlistsIndex()
        
        if request.method == "GET":
            form.name.data = playlist.name
            form.playWatchedStreams.data = playlist.playWatchedStreams
            form.allowDuplicates.data = playlist.allowDuplicates
            form.description.data = playlist.description
            form.favorite.data = playlist.favorite
            form.sortOrder.data = playlist.sortOrder
        elif request.method == "POST" and form.validate_on_submit():
            updateResult = updatePlaylistUseCase.execute(
                playlist_id=id,
                name=form.name.data,
                description=form.description.data or None,
                play_watched_streams=form.playWatchedStreams.data,
                allow_duplicates=form.allowDuplicates.data,
                favorite=form.favorite.data,
                sort_order=form.sortOrder.data
            )
            flash(f"Updated playlist: {updateResult.name}", "success")
            return playlistsDetails(id)
    except Exception as e:
        errorMessage = f"Error updating playlist: {str(e)}"
        flash(errorMessage, "error")
    
    return render_template("form.html", title=f"Edit {playlist.name if 'playlist' in locals() and playlist else id}", form=form, errorMessage=errorMessage)

@app.route("/playlists/delete/<id>", methods=["GET", "POST"])
def playlistsDelete(id: str):
    try:
        playlist = playlistRepository.get_by_id(id)
        if not playlist:
            flash(f"Playlist {id} was not found.", "error")
            return playlistsDetails(id)
        
        if request.method == "POST":
            deletePlaylistUseCase.execute(id)
            flash(f"Deleted '{playlist.name}' successfully.", "success")
            return playlistsIndex()
    except Exception as e:
        flash(f"Error deleting playlist: {str(e)}", "error")

    return render_template("confirm_action.html", 
                           title="Confirm Delete", 
                           message=f"Are you sure you want to delete '{playlist.name if 'playlist' in locals() else id}'?",
                           action_url=url_for("playlistsDelete", id=id),
                           request=request)

@app.route("/queueStreams")
def queueStreamsIndex():
    queueStreams = getAllQueueStreamsUseCase.execute()
    return render_template("queueStreams/index.html", queueStreams= queueStreams)

@app.route("/queueStreams/<id>")
def queueStreamsDetails(id: str):
    queueStream = getQueueStreamDetailsUseCase.execute(id)
    playlists = playlistRepository.get_all_sorted()
    return render_template("queueStreams/details.html", queueStream= queueStream, playlists= playlists)

@app.route("/queueStreams/create/<playlistId>", methods=["GET", "POST"])
def queueStreamsCreate(playlistId: str):
    playlist = playlistRepository.get_by_id(playlistId)
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
                backgroundContent = form.background_content.data,
                playtimeSeconds = form.playtimeSeconds.data,
                remoteId = form.remoteId.data
            )
            
            createResult = createQueueStreamUseCase.execute(
                name=queueStream.name,
                uri=queueStream.uri,
                is_web=queueStream.isWeb,
                stream_source_id=queueStream.streamSourceId,
                stream_source_name=queueStream.streamSourceName,
                watched=queueStream.watched
            )
            
            if(createResult):
                playlist.streamIds.append(createResult.id)
                playlistRepository.save(playlist)
                return playlistsDetails(playlistId)
    
    return render_template("form.html", title= "Create new QueueStream", form= form, errorMessage= errorMessage)

@app.route("/queueStreams/edit/<id>", methods=["GET", "POST"])
def queueStreamsEdit(id: str):
    errorMessage = None
    form = QueueStreamForm()
    
    try:
        queueStream = getQueueStreamDetailsUseCase.execute(id)
        if(not queueStream):
            flash(f"QueueStream with {id} was not found.", "error")
            return queueStreamsIndex()
        
        if request.method == "GET":
            form.name.data = queueStream.name
            form.uri.data = queueStream.uri
            form.isWeb.data = queueStream.isWeb
            form.streamSourceId.data = queueStream.streamSource.id
            form.streamSourceName.data = queueStream.streamSource.name
            form.watched.data = queueStream.watched
            form.backgroundContent.data = queueStream.background_content
            form.playtimeSeconds.data = queueStream.playtimeSeconds
            form.remoteId.data = queueStream.remoteId
        elif request.method == "POST":
            if(form.validate_on_submit()):
                updateResult = updateQueueStreamUseCase.execute(
                    streamId=id,
                    name=form.name.data,
                    uri=form.uri.data,
                    is_web=form.isWeb.data,
                    stream_source_id=form.streamSourceId.data,
                    stream_source_name=form.streamSourceName.data,
                    watched=form.watched.data
                )
                if(updateResult):
                    return queueStreamsDetails(id)
                    
                errorMessage = f"Could not update QueueStream {id}"
            else:
                errorMessage = "Invalid form values"
    except Exception as e:
        errorMessage = f"Error updating QueueStream: {str(e)}"
        flash(errorMessage, "error")
    
    return render_template("form.html", title= f"Edit {queueStream.name}", form= form, errorMessage= errorMessage)

@app.route("/queueStreams/delete/<id>", methods=["GET", "POST"])
def queueStreamsDelete(id: str):
    try:
        queueStream = getQueueStreamDetailsUseCase.execute(id)
        if not queueStream:
            flash(f"QueueStream {id} was not found!", "error")
            return queueStreamsIndex()

        if request.method == "POST":
            deleteQueueStreamUseCase.execute(id)
            flash(f"Deleted '{queueStream.name}' successfully.", "success")
            return queueStreamsIndex()
    except Exception as e:
        flash(f"Error deleting QueueStream: {str(e)}", "error")

    return render_template("confirm_action.html", 
                           title="Confirm Delete", 
                           message=f"Are you sure you want to delete '{queueStream.name if 'queueStream' in locals() else id}'?",
                           action_url=url_for("queueStreamsDelete", id=id),
                           request=request)
    
@app.route("/streamSources")
def streamSourcesIndex():
    streamSources = getAllStreamSourcesUseCase.execute()
    return render_template("streamSources/index.html", streamSources= streamSources)

@app.route("/streamSources/<id>")
def streamSourcesDetails(id: str):
    streamSource = getStreamSourceDetailsUseCase.execute(id)
    return render_template("streamSources/details.html", streamSource= streamSource)

@app.route("/streamSources/create/<playlistId>", methods=["GET", "POST"])
def streamSourcesCreate(playlistId: str):
    playlist = playlistRepository.get_by_id(playlistId)
    if(not playlist):
        flash(f"Playlist {playlistId} was not found.", "error")
        return streamSourcesIndex()
    
    errorMessage = None
    form = StreamSourceForm()
    form.streamSourceTypeId.choices = [(t.value, t.name) for t in StreamSourceType]
    
    if request.method == "POST" and form.validate_on_submit():
        try:
            createResult = createStreamSourceUseCase.execute(
                name=form.name.data,
                uri=form.uri.data,
                is_web=form.isWeb.data,
                stream_source_type_id=form.streamSourceTypeId.data,
                enable_fetch=form.enableFetch.data
            )
            
            playlist.streamSourceIds.append(createResult.id)
            playlistRepository.save(playlist)
            
            flash(f"Created StreamSource: {createResult.name}", "success")
            return streamSourcesDetails(id=str(createResult.id))
        except Exception as e:
            flash(f"Error creating StreamSource: {str(e)}", "error")
    
    return render_template("form.html", title= "Create new StreamSource", form= form, errorMessage= errorMessage)

@app.route("/streamSources/edit/<id>", methods=["GET", "POST"])
def streamSourcesEdit(id: str):
    errorMessage = None
    form = StreamSourceForm()
    form.streamSourceTypeId.choices = [(t.value, t.name) for t in StreamSourceType]
    
    streamSource = getStreamSourceDetailsUseCase.execute(id)
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
    elif request.method == "POST" and form.validate_on_submit():
        try:
            updateResult = updateStreamSourceUseCase.execute(
                stream_source_id=id,
                name=form.name.data,
                uri=form.uri.data,
                is_web=form.isWeb.data,
                stream_source_type_id=form.streamSourceTypeId.data,
                enable_fetch=form.enableFetch.data
            )
            flash(f"Updated StreamSource: {updateResult.name}", "success")
            return streamSourcesDetails(id)
        except Exception as e:
            errorMessage = f"Error updating StreamSource: {str(e)}"
            flash(errorMessage, "error")
    
    return render_template("form.html", title= f"Edit {streamSource.name}", form= form, errorMessage= errorMessage)

@app.route("/streamSources/delete/<id>", methods=["GET", "POST"])
def streamSourcesDelete(id: str):
    try:
        streamSource = getStreamSourceDetailsUseCase.execute(id)
        if(not streamSource):
            flash(f"StreamSource {id} was not found.", "error")
            return streamSourcesDetails(id)
        
        if request.method == "POST":
            deleteStreamSourceUseCase.execute(id)
            flash(f"Deleted '{streamSource.name}' successfully.", "success")
            return streamSourcesIndex()
    except Exception as e:
        flash(f"Error deleting StreamSource: {str(e)}", "error")

    return render_template("confirm_action.html", 
                           title="Confirm Delete", 
                           message=f"Are you sure you want to delete '{streamSource.name if 'streamSource' in locals() else id}'?",
                           action_url=url_for("streamSourcesDelete", id=id),
                           request=request)

@app.route("/play/<playlistId>")
def play(playlistId: str):
    playIndex = int(request.args.get("index", 0))
    watchedId = request.args.get("watchedId", None)
    unwatchId = request.args.get("unwatchId", None)
    back = eval(request.args.get("back", "False"))
    
    if(watchedId): 
        toggleWatchedUseCase.execute(watchedId)
            
    if(unwatchId): 
        toggleWatchedUseCase.execute(unwatchId)
        
    playlistDto = getPlaylistDetailsUseCase.execute(playlistId)
    if(not playlistDto):
        flash(f"Playlist {playlistId} was not found.", "error")
        return index()
    
    playlist = playlistDto.playlist
    queue_streams = playlistDto.queue_streams

    if(playIndex < 0 or playIndex >= len(queue_streams)):
        flash(f"Index was out of range of playlist {playlist.name}, max index: {len(queue_streams) - 1}", "error")
        return playlistsDetails(id = playlist.id)
    
    queueStream = queue_streams[playIndex]
    if(not queueStream):
        flash(f"QueueStream at number {playIndex +1} was not found.", "error")
        return playlistsDetails(id = playlist.id)
    
    if(not back and queueStream.watched and not playlist.playWatchedStreams):
        return redirect(url_for("play", playlistId= playlistId, index= playIndex+1))
    
    embeddedUrl: str = None
    circumventUrl: str = None
    fileUri: str = None
    if(queueStream.isWeb):
        embeddedUrl = playbackService.mapUrlToEmbeddedUrl(queueStream)
            
        circumventUrl = playbackService.getRestrictCircumventedUrl(queueStream)
    else:
        # Abs paths dont work, copy file over?
        # fast api symlink wont work without replacing entire flask
        fileUri = playbackService.mapUrlToEmbeddedUrl(queueStream)
    
    nextQueueStreams = []
    for next_qs in queue_streams[playIndex+1 : playIndex+4]: # Next 4, if any
        if(next_qs):
            nextQueueStreams.append(next_qs)
        
    enumeratedNextQueueStreams = enumerate(nextQueueStreams, playIndex) if nextQueueStreams else None
    return render_template("play.html", playlist= playlist, queueStream= queueStream, index= playIndex, 
        playlists = [p for p in getAllPlaylistsUseCase.execute() if p.id != playlistId],
        embeddedUrl= embeddedUrl, circumventUrl= circumventUrl, fileUri= fileUri, 
        enumeratedNextQueueStreams= enumeratedNextQueueStreams)

@registerTask("fetchPlaylist")
@app.route("/fetch/<playlistId>")
def fetchPlaylist(playlistId):
    playlist = playlistService.get(playlistId)
    if(not playlist):
        flash(f"Playlist {id} was not found.", "error")
        return reloadPage()
    
    flash(f"Fetch running in background...", "info")
    def runFetch():
        try:
            started = getDateTime()
            newQueueStreams = fetchService.fetch(playlist.id, settings.fetchLimitSingleSource, takeNewOnly= True)
            duration = getDateTime() - started # ToHumanReadableString()

            resultsUrl = f"fetch?count={len(newQueueStreams)}&duration={duration}"
            
            # TODO flash and reload are not available in the scope of an async task
            # flash(f"Fetch complete", "success") # TODO make a link with details
            # return reloadPage()
        except Exception as e:
            flash(f"ERROR: {str(e)}", "error")

    threading.Thread(target= runFetch, daemon= True).start()
    
    return reloadPage()

@registerTask("downloadPlaylist")
@app.route("/download/<playlistId>")
def downloadPlaylist(playlistId):
    audioOnly = request.args.get("audioOnly", "false").lower() is True
    playlist = playlistService.get(playlistId)
    if(not playlist):
        flash(f"Playlist {id} was not found.", "error")
        return reloadPage()
    
    flash(f"Download running in background...", "info")
    def runDownload():
        try:
            started = getDateTime()
            
            for i, streamId in enumerate(playlist.streamIds):
                stream = queueStreamService.get(streamId)
                if(not stream.isWeb):
                    printS("Cannot download a non-web stream, \"", stream.name, "\" was skipped.", color = BashColor.WARNING)
                    continue
                
                try:
                    downloadService.download(stream.uri, playlist.name, audioOnly=audioOnly)
                except Exception as e:
                    printS("Failed to download stream \"", stream.name, "\": ", e, color = BashColor.FAIL)
                    continue
            
            duration = getDateTime() - started # ToHumanReadableString()
        except Exception as e:
            flash(f"ERROR: {str(e)}", "error")

    threading.Thread(target= runDownload, daemon= True).start()
    
    return reloadPage()

@app.route("/prune/<playlistId>")
def prunePlaylist(playlistId):
    playlist = playlistService.get(playlistId)
    
    data = sharedService.preparePrune(playlistId)
    pruneResult = sharedService.doPrune(data)
    if(pruneResult):
        # TODO len here is soft deleted, not actually removed ones, gives "wrong" result
        flash(f"Pruned {len(data.queueStreams)} QueueStreams in Playlist {playlist.name}", "success")
    
    return reloadPage()

@app.route("/purge", methods=["GET", "POST"])
def purgeAll():
    if request.method == "POST":
        data = sharedService.preparePurge()
        result = sharedService.doPurge(data)
        if result:
            flash("Purge completed successfully.", "success")
        else:
            flash("Purge failed.", "error")
        return index()

    return render_template("confirm_action.html", 
                           title="Confirm Purge All", 
                           message="Are you sure you want to purge everything? This cannot be undone.",
                           action_url=url_for("purgeAll"),
                           request=request)

@app.route("/softDeleted")
def softDeletedIndex():
    playlists = [e for e in playlistService.getAll(True) if e.deleted]
    queueStreams = [e for e in queueStreamService.getAll(True) if e.deleted]
    streamSources = [e for e in streamSourceService.getAll(True) if e.deleted]
    
    return render_template("softDeleted.html", playlists= playlists, queueStreams= queueStreams, streamSources= streamSources)

@csrf.exempt
@app.route("/addToPlaylist", methods=["POST"])
def addPlaybackStreamsToPlaylists():
    inputData = request.get_json()
    queueStreamId = inputData.get("queueStreamId")
    playlistIds = inputData.get("playlistIds")

    if not queueStreamId or not playlistIds:
        flash(f"Failed to copy QueueStream, queueStreamId or playlistIds missing.", "error")
        return jsonify({"result": False, "error": "Missing IDs"}), 400
    
    queueStream = queueStreamService.get(queueStreamId)
    if not queueStream:
        flash(f"Failed to copy QueueStream, queueStream not found.", "error")
        return jsonify({"result": False, "error": "QueueStream not found"}), 404

    result = playbackService.addPlaybackStreamToPlaylist(queueStream, playlistIds)
    successCount = len(result)
    flash(f"Copied QueueStream to {successCount} Playlists.", "success")
    
    return jsonify({
        "result": successCount > 0,
        "addedCount": successCount,
        "totalRequested": len(playlistIds)
    })

def addPlaybackStreamToPlaylist(playlistId, queueStreamId):
    playlist = playlistService.get(playlistId)
    if(not playlist):
        flash(f"Playlist {id} was not found.", "error")
        return
    
    queueStream = queueStreamService.get(queueStreamId)
    if(not queueStream):
        flash(f"QueueStream {id} was not found.", "error")
        return
    
    result = playbackService.addPlaybackStreamToPlaylist(playlistId, queueStream)
    
    if(result):
        flash(f"Added to {playlist.name}", "success")
    else:
        flash(f"Failed adding to {playlist.name}", "error")
        
    return jsonify({"result": result})
    
if __name__ == "__main__":
    # print("Routes:")
    # for rule in app.url_map.iter_rules():
    #     print(f"{rule.rule} - {rule.methods} - {rule.endpoint}")
    
    app.run(host= "0.0.0.0", port= 8888)