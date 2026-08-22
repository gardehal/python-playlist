# Change Plan: Transition to Hexagonal Architecture

**Reasoning**: 
- The current architecture is a "monolithic" layered structure where business logic, Flask routing, and data access are tightly coupled. A transition to Hexagonal Architecture will decouple these concerns, making the system easier to test and more flexible to infrastructure changes (like switching storage or providers).

**Objective**: 
- Reorganize the project into three distinct layers: **Domain** (Core Logic), **Application** (Use Cases/Ports), and **Infrastructure** (Adapters for Web, CLI, and Data).

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

2. **Phase 2: The Application Layer (The Use Cases)**
   - **[services/]**
     - [Action]: Refancor existing services into "Use Case Interactors".
     - [Logic]: Instead of `PlaylistService.add(playlist)`, create a use case like `AddStreamToPlaylistUseCase`. This class will take the `Repository` port as a dependency and orchestrate the domain logic.

3. **Phase 3: The Infrastructure Layer (The Adapters)**
   - **[new: infrastructure/repositories/]**
     - [Action]: Move current data access logic from `services/` to here.
     - [Logic]: Implement the concrete versions of the ports defined in Phase 1 (e.g., `JsonPlaylistRepository`).
   - **[new: infrastructure/providers/]**
     - [Action]: Isolate external fetching/downloading logic.
     - [Logic]: Create adapters for YouTube, Local Filesystem, etc., which implement the `StreamProvider` port.

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
- Created new plan file with refined architectural strategy, interview context, and finalized port structure.

# Verification Report
*(To be completed after implementation)*
