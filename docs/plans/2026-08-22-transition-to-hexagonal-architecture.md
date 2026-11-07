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

- [ ] Add unit tests for use cases using mocked/stubbed Ports.
- [ ] Wire provider adapters through Ports; services still call yt-dlp directly.
- [ ] Add the local-filesystem provider adapter described in the Infrastructure phase.
- [ ] Complete Flask and CLI driving-adapter wiring; `server.py` and `Main.py` still instantiate services directly.
- [ ] Implement a Composition Root for dependency injection of adapters into use cases.

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

## Validation

- Previously verified: `StreamSource` and `QueueStream` lifecycle use cases work.
- Previously verified: Domain exceptions are raised and handled in use cases.
- Validation for the remaining Legacy Todos has not yet been performed.

## Results

- Kept `Playlist`, `QueueStream`, and `StreamSource` free of Flask and `BaseService` imports.
- Defined repository Ports for `Playlist`, `StreamSource`, and `QueueStream`.
- Created the Domain Exception hierarchy.
- Implemented `BaseService` repository adapters for `Playlist`, `StreamSource`, and `QueueStream`.
- Implemented `StreamSource` lifecycle use cases (`Create`, `Update`, `Delete`).
- Implemented `QueueStream` lifecycle use cases (`Create`, `Update`, `Delete`).
- Implemented `CreatePlaylistFromYoutubeUseCase` and `ToggleQueueStreamWatchedUseCase`.
