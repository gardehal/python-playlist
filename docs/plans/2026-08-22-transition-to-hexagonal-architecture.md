# Transition to Hexagonal Architecture

## Problem

Business logic, Flask routes, CLI controllers, and data access began in a tightly coupled layered structure. This plan tracks only the Hexagonal Ports-and-Adapters transition: separating Domain, Application, Infrastructure, and driving-adapter responsibilities so business logic can be tested independently and infrastructure can change with less coupling.

## Decisions

- D1: Use a small-to-large strategy, tackling one entity at a time.
- D2: Keep Domain objects simple; the goal is restructuring, not deep object-logic refactoring.
- D3: Define Ports before implementing adapters.
- D4: Use one file per Port to follow SRP and keep dependencies clean.
- D5: Do not add stub implementations during the Port-definition phase.
- D6: Wrap the existing JSON repository behavior inside Infrastructure adapters.
- D7: Refactor entities in this order: `StreamSource`, `QueueStream`, then `Playlist`.

## Approach

1. **Domain and Ports:** Keep `Playlist`, `QueueStream`, and `StreamSource` free of Flask/database-specific logic. Define repository/provider ABCs in individual files and map infrastructure errors to Domain exceptions.
2. **Application:** Refactor services into use cases that depend on Ports; test use-case logic with Port mocks/stubs.
3. **Infrastructure:** Implement repository adapters around existing `BaseService` logic and isolate external integrations behind provider adapters.
4. **Presentation:** Refactor Flask routes and CLI controllers as driving adapters that handle input/output and invoke Application use cases.
5. **Application wiring:** Add a Composition Root to inject adapters into use cases.

## Todos

- [x] Add Port-stub unit tests for QueueStream and StreamSource lifecycle use cases.
- [x] Add Port-stub tests for all current use cases, including Playlist lifecycle/read paths, missing records, add-stream rules, watched toggling, and provider-backed import.
- [x] Implement YouTube playlist extraction behind `ExternalStreamProvider` and persist fetched entries in `CreatePlaylistFromYoutubeUseCase`.
- [x] Add provider-backed playlist import tests for empty entries and provider errors.
- [x] Verify and document how repository `save()` assigns IDs; playlist import reads each saved `QueueStream.id` to link it to the playlist.
- [x] Replace abstract repository construction and fix use-case constructor arities in `server_refactor.py`'s module-level wiring.
- [x] Migrate `server_refactor.py` routes to application use cases and Ports; no direct repository or legacy-service references remain in the routes.
- [x] Resolve the `CreateStreamSourceUseCase` validation contract using the form's name/URI length limits, optional URI behavior, and supported source type IDs.
- [ ] Replace the transitional fetch service adapter with a provider-native implementation; playlist import uses `YoutubeProvider`.
- [x] Replace the transitional download service adapter with `YtDlpStreamDownloadProvider` and preserve playlist output directories plus audio/video format selection.
- [ ] Complete Flask and CLI cutovers; `server.py` and `Main.py` remain active, and `Main_refactor.py` still lacks parity for several legacy commands.
- [x] Implement `CompositionRoot` and use it to wire repositories, `YoutubeProvider`, and use cases in `server_refactor.py`.

## Legacy Todos

Original file checklist retained as an historical snapshot; current status is tracked above and in Results.

- [ ] `model/` (Refactor entities to be pure Domain objects)
- [ ] `services/` (Convert into Application Use Case layer)
- [ ] `server.py` & `controllers/` (Convert into Driving Adapters for Web)
- [ ] `controllers/` (Convert existing CLI controllers into Driving Adapters for CLI)
- [ ] New `ports/` directory (Define individual Abstract Base Classes per Port file)
- [ ] New `infrastructure/repositories/` directory (Implement concrete data access adapters)
- [ ] New `infrastructure/providers/` directory (Implement concrete external service adapters)

## Notes / considerations

- The completed Ports, repository adapters, Domain exceptions, and use cases are recorded under Results.
- Broader README refactoring todos remain separate tasks and are not tracked in this Hexagonal plan.
- JSON files remain the data store behind repository adapters.
- `GetPlaylistDetailsUseCase` previously called `get_by_playlist_id`, which the declared Ports and adapters do not provide. It now resolves the IDs held by `Playlist` using `get_by_id`, preserving playlist order and skipping missing related records.
- `GetAllPlaylistsUseCase` previously called `getAllSorted()`, which is not part of `PlaylistRepository`; it now sorts `get_all()` results using the legacy favorite/sortOrder/name rule.
- `GetAllStreamSourcesUseCase` previously imported its repository type through the Infrastructure adapter module; it now imports the Port directly.
- Repository adapter integration tests verified that `BaseService.add()` assigns IDs, repeat `save()` updates existing records, and `delete()` soft-deletes them. The Ports document the ID assignment contract.
- `ports/playlist_repository.py` previously imported `model.playlist`; the actual module is `model.Playlist`. This prevented importing use cases on the current environment and is now corrected.
- `server_refactor.py` previously wired abstract Port types as repositories and passed mismatched constructor arguments; module-level repository/use-case construction is now corrected.
- All `server_refactor.py` routes use CompositionRoot use cases; fetch temporarily uses a lazy Infrastructure adapter around the existing service.
- `Main_refactor.py` is a parallel CompositionRoot-backed CLI entrypoint with no service/controller imports. It handles commands with existing use cases and explicitly reports unmigrated legacy-only commands; it is not yet a drop-in replacement for `Main.py`.
- The local-filesystem provider adapter is deferred at the user's request because the original implementation did not work; it is excluded from active Todos.
- `CreateStreamSourceUseCase` trims and requires a name, enforces the form's 200-character name/URI limits, permits an empty optional URI, normalizes numeric-string type IDs, and accepts only type ID `0` or declared `StreamSourceType` values.
- `CreatePlaylistFromYoutubeUseCase` relies on `QueueStreamRepository.save()` assigning an ID to the entity; this behavior is now verified against the real JSON adapter.
- Empty provider results create an empty playlist; provider errors propagate before any playlist or stream persistence.

## Validation

- Previously verified: `StreamSource` and `QueueStream` lifecycle use cases work.
- Previously verified: Domain exceptions are raised and handled in use cases.
- `python -m unittest discover -s tests -p "test_use_case_ports.py" -q` passed 63 tests covering use cases, CompositionRoot, repository adapters, provider normalization, Flask routes, and `Main_refactor.py` use-case dispatch.
- `python -m compileall -q Main_refactor.py composition_root.py server_refactor.py application/use_cases ports infrastructure/providers` passed.
- `python Main_refactor.py -help > $null` exited successfully.
- External media downloads are not exercised end to end; fetch still uses a transitional adapter around the legacy service.

## Results

- Kept `Playlist`, `QueueStream`, and `StreamSource` free of Flask and `BaseService` imports.
- Defined repository Ports for `Playlist`, `StreamSource`, and `QueueStream`.
- Created the Domain Exception hierarchy.
- Implemented `BaseService` repository adapters for `Playlist`, `StreamSource`, and `QueueStream`.
- Implemented `StreamSource` lifecycle use cases (`Create`, `Update`, `Delete`).
- Added `StreamSourceError` validation to `CreateStreamSourceUseCase` and tests for blank/oversized names, optional URI, URI length, and source type normalization/rejection.
- Implemented `QueueStream` lifecycle use cases (`Create`, `Update`, `Delete`).
- Implemented `ToggleQueueStreamWatchedUseCase`.
- Implemented the five read-use-case tests; fixed `GetAllPlaylistsUseCase` to use/sort the declared `get_all` Port method and corrected `GetAllStreamSourcesUseCase` to depend on its Port.
- Repaired all three BaseService repository adapters to use supported public methods, upsert existing entities, and apply soft-delete filtering.
- Added temporary-storage integration tests for repository ID assignment, create/read/update/list, and soft delete behavior.
- Implemented YouTube flat-playlist extraction in `YoutubeProvider.fetch_playlist` and verified `CreatePlaylistFromYoutubeUseCase` links IDs that reload through the real JSON adapters.
- Tested empty YouTube playlist results and provider failures; failures do not persist partial playlist data.
- Added `composition_root.py` to centralize repository, provider, and use-case construction; `server_refactor.py` now consumes it.
- Corrected `server_refactor.py` to construct concrete repository adapters and match use-case constructor signatures.
- Wired QueueStream web edit to `UpdateQueueStreamUseCase` for source metadata, watched/background flags, playtime, and remote ID; added a route regression test alongside create coverage.
- Imported `StreamSourceType` explicitly in `server_refactor.py` and added a Flask test for loading the StreamSource create form; both StreamSource handlers depend on those enum choices.
- Migrated the home route to the injected playlist repository and initialized `Settings` in `server_refactor.py`.
- Added playlist lookup and StreamSource-to-playlist link use cases; removed direct repository access from `server_refactor.py` routes.
- Added `CopyQueueStreamToPlaylistsUseCase` to preserve the legacy per-playlist QueueStream clone behavior and URI/name duplicate filtering; wired the copy endpoint through CompositionRoot.
- Extended repository Ports with deleted-record listing and permanent removal; migrated prune, purge, and soft-deleted listing to application use cases.
- Added a pure playback URL use case and migrated `/play` away from `PlaybackService`.
- Added fetch/download Ports, use cases, and lazy Infrastructure adapters; migrated the corresponding async routes off direct legacy service globals.
- Replaced the legacy download adapter with `YtDlpStreamDownloadProvider`, which selects audio/video formats and saves under a sanitized playlist directory; verified its yt-dlp options and output path with a fake client.
- Added `Main_refactor.py`, which parses the existing CLI commands and dispatches supported operations through an injected `CompositionRoot`; unmigrated commands are reported rather than delegated to legacy controllers.
- Added `tests/test_use_case_ports.py` with Port-stub tests across QueueStream, StreamSource, Playlist, and YouTube playlist import use cases.
- Fixed `GetPlaylistDetailsUseCase` to use declared `get_by_id` Port methods and corrected the `Playlist` model import case in `ports/playlist_repository.py`.
