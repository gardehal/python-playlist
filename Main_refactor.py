import os
import sys
import webbrowser
from types import SimpleNamespace
from urllib.parse import urlparse
from typing import Optional, Sequence

from Argumentor import Argumentor
from Commands import Commands
from Settings import Settings
from composition_root import CompositionRoot
from enums.CommandHitValues import CommandHitValues
from enums.StreamSourceType import StreamSourceTypeUtil
from grdUtil.FileUtil import makeFiles
from grdUtil.InputUtil import getIdsFromInput
from grdUtil.PrintUtil import printLists, printS
from grdUtil.StaticUtil import StaticUtil


class MainRefactor:
    def __init__(
        self,
        composition_root: Optional[CompositionRoot] = None,
        settings: Optional[Settings] = None,
        commands: Optional[Commands] = None,
    ) -> None:
        self.application = composition_root or CompositionRoot()
        self.settings = settings or Settings()
        self.commands = commands or Commands()

    def run(self, argv: Optional[Sequence[str]] = None) -> None:
        makeFiles(self.settings.watchedLogFilepath)
        argumentor = self.commands.getArgumentor()
        results = argumentor.validate(list(argv) if argv is not None else sys.argv)

        if not results:
            print("No valid command was found, please consult the manual for available commands.")
            print(argumentor.getSyntaxDescription())
            return

        for result in results:
            if not result.isValid:
                print(f"Input for {result.commandName} was not valid:")
                print(result.getFormattedMessages())
                continue

            if result.messages:
                print(f"Command {result.commandName} was accepted with modifications:")
                print(result.getFormattedMessages())

            try:
                self._dispatch(result, argumentor)
            except Exception as error:
                printS(f"Command {result.commandName} failed: {error}")

    def _dispatch(self, result, argumentor: Argumentor) -> None:
        command = result.commandHitValue
        arguments = result.arguments

        if command == CommandHitValues.HELP:
            print(argumentor.getFormattedDescription())
        elif command == CommandHitValues.TEST:
            printS("Test")
        elif command == CommandHitValues.EDIT:
            playlist_id = self._resolve_playlist_ids(arguments[self.commands.playlistIdsArgumentName])[0]
            filepath = os.path.join(self.settings.localStoragePath, "Playlist", f"{playlist_id}.json")
            if not hasattr(os, "startfile"):
                raise OSError("Opening playlist files is supported only on Windows.")
            os.startfile(os.path.abspath(filepath))
        elif command == CommandHitValues.LIST_SETTINGS:
            print(self.settings.getAllSettingsAsTable())
        elif command == CommandHitValues.ADD_PLAYLIST:
            playlist = self.application.create_playlist.execute(
                name=arguments[self.commands.entityNameArgumentName],
                play_watched_streams=arguments[self.commands.playWatchedStreamsFlagName],
                allow_duplicates=arguments[self.commands.allowDuplicatesFlagName],
            )
            for stream_source_id in arguments[self.commands.streamSourceIdsArgumentName]:
                self.application.add_stream_source_to_playlist.execute(playlist.id, stream_source_id)
            printS(f'Playlist "{playlist.name}" added successfully.')
        elif command == CommandHitValues.ADD_PLAYLIST_FROM_YOUTUBE:
            playlist = self.application.create_playlist_from_youtube.execute(
                url=arguments[self.commands.uriArgumentName][0],
                name=arguments[self.commands.entityNameArgumentName],
                play_watched_streams=arguments[self.commands.playWatchedStreamsFlagName],
                allow_duplicates=arguments[self.commands.allowDuplicatesFlagName],
            )
            printS(f'Playlist "{playlist.name}" added from YouTube.')
        elif command == CommandHitValues.DELETE_PLAYLIST:
            playlist_ids = self._resolve_playlist_ids(arguments[self.commands.playlistIdsArgumentName])
            for playlist_id in playlist_ids:
                self.application.delete_playlist.execute(playlist_id)
            printS(f"Deleted {len(playlist_ids)} playlist(s).")
        elif command == CommandHitValues.LIST_PLAYLISTS:
            playlists = self.application.get_all_playlists.execute()
            if arguments[self.commands.includeSoftDeletedFlagName]:
                deleted = self.application.get_soft_deleted_entities.execute().playlists
                playlists = playlists + deleted
            printLists([[playlist.summaryString() for playlist in playlists]], [f"{len(playlists)} Playlists"])
        elif command == CommandHitValues.DETAILS_PLAYLIST:
            playlist_ids = self._resolve_playlist_ids(arguments[self.commands.playlistIdsArgumentName])
            for playlist_id in playlist_ids:
                details = self.application.get_playlist_details.execute(playlist_id)
                if details is None:
                    printS(f"Playlist {playlist_id} was not found.")
                    continue
                playlist = details.playlist
                printS(playlist.detailsString(
                    includeUri=arguments[self.commands.includeUriFlagName],
                    includeId=arguments[self.commands.includeIdFlagName],
                    includeDatetime=arguments[self.commands.includeDateTimeFlagName],
                    includeListCount=arguments[self.commands.includeListCountFlagName],
                ))
                for stream in details.queue_streams:
                    printS(stream.detailsString(
                        includeUri=arguments[self.commands.includeUriFlagName],
                        includeId=arguments[self.commands.includeIdFlagName],
                        includeDatetime=arguments[self.commands.includeDateTimeFlagName],
                    ))
                if arguments[self.commands.includeSourceFlagName]:
                    for source in details.stream_sources:
                        printS(source.detailsString(
                            includeUri=arguments[self.commands.includeUriFlagName],
                            includeId=arguments[self.commands.includeIdFlagName],
                            includeDatetime=arguments[self.commands.includeDateTimeFlagName],
                        ))
        elif command == CommandHitValues.FETCH_PLAYLIST:
            playlist_ids = self._resolve_playlist_ids(arguments[self.commands.playlistIdsArgumentName])
            take_after = arguments[self.commands.takeAfterArgumentName]
            take_before = arguments[self.commands.takeBeforeArgumentName]
            if take_after is not None or take_before is not None:
                printS("Fetch date ranges are not supported by the current provider Port.")
                return
            for playlist_id in playlist_ids:
                streams = self.application.fetch_playlist.execute(
                    playlist_id,
                    self.settings.fetchLimitSingleSource,
                    take_new_only=arguments[self.commands.takeAllFlagName],
                )
                printS(f"Fetched {len(streams)} stream(s) for playlist {playlist_id}.")
        elif command == CommandHitValues.PRUNE_PLAYLIST:
            if arguments[self.commands.includeSoftDeletedFlagName] or arguments[self.commands.permanentlyDeleteFlagName]:
                printS("Prune options for deleted or permanent records are not supported by the current use case.")
                return
            for playlist_id in self._resolve_playlist_ids(arguments[self.commands.playlistIdsArgumentName]):
                if not self._confirm(f"Prune watched streams from playlist {playlist_id}?"):
                    continue
                streams = self.application.prune_watched_queue_streams.execute(playlist_id)
                printS(f"Pruned {len(streams)} stream(s) from playlist {playlist_id}.")
        elif command == CommandHitValues.PURGE:
            if self._confirm("Permanently remove all soft-deleted entities?"):
                self.application.purge_soft_deleted_entities.execute()
                printS("Purge completed.")
        elif command == CommandHitValues.DOWNLOAD_PLAYLIST:
            if self._has_download_options(arguments):
                printS("Custom download ranges, names, and output directories are not supported by the current use case.")
                return
            for playlist_id in self._resolve_playlist_ids(arguments[self.commands.playlistIdsArgumentName]):
                result = self.application.download_playlist.execute(playlist_id)
                printS(
                    f"Downloaded {result.downloaded_count}; skipped {result.skipped_count}; "
                    f"failed {result.failed_count}."
                )
        elif command in (CommandHitValues.ADD_STREAM, CommandHitValues.ADD_MULTIPLE_STREAMS):
            playlist_id = self._resolve_playlist_ids(arguments[self.commands.playlistIdsArgumentName])[0]
            uris = arguments[self.commands.uriArgumentName]
            requested_name = arguments[self.commands.entityNameArgumentName]
            for uri in uris:
                name = requested_name or self._name_from_uri(uri)
                stream = self.application.create_queue_stream.execute(
                    name=name,
                    uri=uri,
                    is_web=urlparse(uri).scheme.lower() in {"http", "https"},
                )
                self.application.add_stream_to_playlist.execute(playlist_id, stream.id)
                printS(f'Added stream "{stream.name}" to playlist {playlist_id}.')
        elif command == CommandHitValues.ADD_SOURCE:
            if arguments[self.commands.backgroundContentFlagName]:
                printS("Background-content sources are not supported by the current create use case.")
                return
            playlist_id = self._resolve_playlist_ids(arguments[self.commands.playlistIdsArgumentName])[0]
            uri = arguments[self.commands.uriArgumentName][0]
            source_type = StreamSourceTypeUtil.strToStreamSourceType(uri)
            if source_type is None:
                printS(f"Could not determine stream source type for {uri}.")
                return
            name = arguments[self.commands.entityNameArgumentName] or self._name_from_uri(uri)
            source = self.application.create_stream_source.execute(
                name=name,
                uri=uri,
                is_web=urlparse(uri).scheme.lower() in {"http", "https"},
                stream_source_type_id=source_type.value,
                enable_fetch=arguments[self.commands.enableFetchFlagName],
            )
            self.application.add_stream_source_to_playlist.execute(playlist_id, source.id)
            printS(f'Added stream source "{source.name}" to playlist {playlist_id}.')
        elif command == CommandHitValues.LIST_SOURCES:
            sources = self.application.get_all_stream_sources.execute()
            if arguments[self.commands.includeSoftDeletedFlagName]:
                sources += self.application.get_soft_deleted_entities.execute().streamSources
            printLists([[source.summaryString() for source in sources]], [f"{len(sources)} StreamSources"])
        elif command == CommandHitValues.OPEN_SOURCE:
            sources = self.application.get_all_stream_sources.execute()
            source_ids = getIdsFromInput(
                arguments[self.commands.streamSourceIdsArgumentName],
                [source.id for source in sources],
                sources,
                startAtZero=False,
                debug=self.settings.debug,
            )
            for source_id in source_ids:
                source = self.application.get_stream_source_details.execute(source_id)
                if source is not None:
                    webbrowser.open(source.uri)
        elif command == CommandHitValues.LIST_SOFT_DELETED:
            entities = self.application.get_soft_deleted_entities.execute()
            simplified = arguments[self.commands.simplifiedPrintFlagName]
            formatter = (lambda entity: entity.summaryString()) if simplified else (lambda entity: entity.detailsString())
            printLists(
                [
                    [formatter(entity) for entity in entities.playlists],
                    [formatter(entity) for entity in entities.queueStreams],
                    [formatter(entity) for entity in entities.streamSources],
                ],
                ["playlists", "queueStreams", "streamSources"],
            )
        else:
            printS(f"Command {result.commandName} is not migrated to the Hexagonal CLI yet.")

    def _resolve_playlist_ids(self, requested_ids):
        playlists = self.application.get_all_playlists.execute()
        return getIdsFromInput(
            requested_ids,
            [playlist.id for playlist in playlists],
            playlists,
            startAtZero=False,
            debug=self.settings.debug,
        )

    def _name_from_uri(self, uri: str) -> str:
        parsed_uri = urlparse(uri)
        name = os.path.basename(parsed_uri.path.rstrip("/"))
        return name or uri

    def _has_download_options(self, arguments) -> bool:
        return any((
            arguments[self.commands.directoryNameArgumentName] is not None,
            arguments[self.commands.startIndexArgumentName] != 0,
            arguments[self.commands.endIndexArgumentName] is not None,
            arguments[self.commands.streamNameRegexArgumentName] is not None,
            arguments[self.commands.useIndexFlagName],
        ))

    @staticmethod
    def _confirm(message: str) -> bool:
        printS(message, " (y/n): ")
        return input().strip().lower() in StaticUtil.affirmative


if __name__ == "__main__":
    MainRefactor().run()
