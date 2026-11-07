# Change Plan: Transition to Hexagonal Architecture

**Reasoning**: 
- The current architecture is a "monolithic" layered structure where business logic, Flask routing, and data access are tightly coupled. A transition to Hexagonal Architecture will decouple these concerns, making the system easier to test and more flexible to infrastructure changes (like switching storage or providers).

**Objective**: 
- Reorganize the project into three distinct layers: **Domain** (Core Logic), **Application** (Use Cases/Ports), and **Infrastructure** (Adapters for Web, CLI, and Data).
- Implement a **Composition Root** to handle dependency injection of adapters into use cases.
- Establish a **Domain Exception** hierarchy to decouple error handling from infrastructure details.

**Files to Modify**:
- [ ] `model/` (Refactor entities to be pure Domain objects)
- [ ] `services/` (Convert into Application Use Case layer)
- [ ] `server.py` & `controllers/` (Convert into Driving Adapters for Web)
- [ ] `controllers/` (Convert existing CLI controllers into Driving Adaps for CLI)
- [ ] New `ports/` directory (Define individual Abstract Base Classes per Port file)
- [ ] New `infrastructure/repositories/` directory (Implement concrete data access adapters)
- [ ] New `infrastructure/providers/` directory (Implement concrete external service adapters)

**Detailed Steps**:

1. **Phase 1: The Domain & Port Definition (The Core)**
   - **[model/]**
     - [Action]: Refactor `Playlist`, `QueueStream`, and `StreamSource`.
     - [Logic]: Remove any Flask-specific or database-specific logic/imports. Ensure they are pure Python objects containing only business rules.
   - **[new: ports/]**
     - [Action]: Create individual files for each Port (e.g., `stream_source_repository.py`).
     - [Logic]: Define the Abstract Base Classes (ABCs) to establish the "contracts" the rest of the app must follow.
   - **[new: exceptions/]**
     - [Action]: Define a hierarchy of Domain Exceptions.
     - [Logic]: Ensure infrastructure adapters map their specific errors (e.g., `FileNotFoundError`) to these domain-level exceptions.

2. **Phase 2: The Application Layer (The Use Cases)**
   - **[services/]**
     - [Action]: Refactor existing services into "Use Case Intermountable".
     - [Logic]: Instead of `PlaylistService.add(playlist)`, create a use case like `AddStreamToPlaylistUseCase`. This class will take the `Repository` port as a dependency and orchestrate the domain logic.
   - **[testing]**
     - [Action]: Write unit tests for Use Cases using Mocks/Stubs of the Ports.
     - [Logic]: Verify business logic in isolation before implementing concrete adapters.

3. **Phase 3: The Infrastructure Layer (The Adapters)
   - **[new: infrastructure/repositories/]**
     - [Action]: Implement concrete versions of the ports.
     - [Logic]: Initially, wrap `BaseService` logic to provide a familiar implementation while adhering to the new Port interfaces. This allows us to leverage existing file-system logic without leaking it into the Application layer.
   - **[new: infrastructure/providers/]**
     - [Action]: Isolate external fetching/downloading logic.
     - [Logic]: Create adapters for YouTube, Local Filesystem, etc., which implement the `ExternalStreamProvider` port.

4. **Phase 4: The Presentation Layer (The Entry Points)**
   * **[server.py & controllers/]**
     * [Action]: Refactor Flask routes and CLI controllers.
     * [Logic]: These become "Driving Adapters". They should only handle HTTP/CLI input, call a Use Case from the Application layer, and return a response.

**Note**: We will proceed **entity by entity**, starting with `StreamSource`, then moving to `QueueStream`, and finally `Playlist`. We will define all **Ports** first in Phase 1 as individual files before refactoring implementations in later steps.

# Interview Context

**Q: How should we handle the transition complexity?**
A: Start with a "Small-to-Large" strategy, tackling one entity at a $\text{time}$ to maintain control.

**Q: How will we handle data storage (currently JSON files)?**
A: We will use the existing repository-like logic directly within the new Infrastructure/Repository adapters.

**Q: What is the desired level of "Python Magic" in the Domain layer?**
A: Keep it as simple as possible for now; the primary goal of this round is restructuring, not deep refactoring of the object logic itself.

**Q: Should we define interfaces or implement them immediately?**
A: Define the Ports (Interfaces) first, then move to implementation as a later step.

**Q: How should the `ports/` directory be structured?**
A: One file per Port (e.g., `stream_source_repository.py`) to follow SRP and keep dependencies clean.

**Q: Should we implement "Stub" implementations during Phase 1?**
A: No, define the interfaces first (Option A) to establish the contract before moving to implementation.

# Execution Summary
- [DONE] Defined all Repository Ports (`Playlist`, `Stream_Source`, `QueueStream`).
- [DONE] Created Domain Exception hierarchy.
- [DONE] Implemented Infrastructure Adapters (Wrappers) using `BaseService` for `Playlist`, `StreamSource`, and `QueueStream`.
- [DONE] Implemented Application Use Cases for `StreamSource` (`Create`, `Update`, `Delete`).
- [DONE] Implemented Application Use Cases for `QueueStream` (`Create`, `Update`, `Delete`).
- [DONE] Implemented orchestration Use Cases: `CreatePlaylistFromYoutubeUseCase` and `ToggleQueueStreamWatchedUseCase`.

# Verification Report
- [VERIFIED] `StreamSource` lifecycle works via new use cases.
- [VERIFIED] `QueueStream` lifecycle works via new use cases.
- [VERIFIED] Domain exceptions are correctly raised and handled in Use Cases.
