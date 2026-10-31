# Tasks: Upgrade do moinho

**Input**: Design documents from `specs/002-upgrade-moinho/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/socketio-events.md`, `quickstart.md`

**Tests**: Test tasks are included because the project constitution requires
business-rule coverage, including rejection and concurrent-request cases.

**Organization**: Tasks are grouped by user story. This feature has one
independently testable user story.

## Phase 1: Setup

**Purpose**: Project initialization and shared infrastructure.

No setup tasks are needed: the existing Python server, Vue client, Socket.IO
events, and `unittest` suite already provide the required infrastructure.

---

## Phase 2: Foundational

**Purpose**: Blocking prerequisites for user-story implementation.

No foundational changes are needed. The feature uses the existing shared
village state, player roles, season lifecycle, and event helpers.

---

## Phase 3: User Story 1 - Aprimorar o moinho (Priority: P1) 🎯 MVP

**Goal**: Let the Mestre pay to raise the mill level and synchronize the
resulting flour production with all players.

**Independent Test**: Start a season at mill level 1; as Mestre, upgrade with
sufficient coins and verify the exact debit, new level, and subsequent flour
production in two clients. Confirm unauthorized, unaffordable, closed-season,
and maximum-level requests are refused without state changes; construction
completion does not increase production.

### Tests for User Story 1

> Write tests first and confirm they fail before implementing the behavior.

- [X] T001 [US1] Add `unittest` coverage in `tests/test_server_bread.py` for initial level and production, each upgrade cost and production rate, exact-balance acceptance, insufficient-funds and non-Mestre refusals, closed-season and level-5 refusals, concurrent requests, and construction completion without a production bonus.

### Implementation for User Story 1

- [X] T002 [US1] Update `server.py` so each season starts with `nivel_moinho` 1 and `producao` 10, flour cycles continue every 5 seconds using the current rate, and construction completion no longer increases `producao`.
- [X] T003 [US1] Add the `moinho.nivel_solicitado` handler in `server.py`; validate Mestre role, open season, level below 5, and sufficient coins, then debit `nivel_moinho * 10`, advance one level, update `producao` to `5 + (5 * novo_nivel)`, and broadcast `moinho.nivel_atualizado`; refuse invalid requests only to the requester without changing state.
- [X] T004 [P] [US1] Update `client/index.html` to show the current mill level and flour per 5-second cycle, expose the upgrade action only to the Mestre, emit `moinho.nivel_solicitado`, and update the Vue/Phaser presentation from server snapshots and `moinho.nivel_atualizado`.

**Checkpoint**: The Mestre can upgrade the mill, all clients show the same
authoritative state, and all specified rejection and construction cases pass.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Verify the full implementation and the documented manual flow.

- [X] T005 Run `python -m unittest discover -s tests` and smoke-test the two-client upgrade flow and role-specific controls from `specs/002-upgrade-moinho/quickstart.md`; fix any regressions in `server.py`, `client/index.html`, or `tests/test_server_bread.py`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No changes required.
- **Foundational (Phase 2)**: No changes required.
- **User Story 1 (Phase 3)**: Can begin immediately after confirming the existing
  infrastructure; no other feature stories are prerequisites.
- **Polish (Phase 4)**: Depends on completion of User Story 1 implementation.

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories; it is the MVP.

### Within User Story 1

- T001 writes the server behavior tests first.
- T002 updates the shared season state and production rules.
- T003 adds the upgrade request handler and depends on the state behavior from
  T002.
- T004 can run in parallel with the test and server tasks because the event
  contract is already defined; the client consumes server snapshots and does
  not commit state.
- T005 runs after all implementation tasks.

### Parallel Opportunities

- T001 (`tests/test_server_bread.py`) and T004 (`client/index.html`) touch
  different files and can proceed in parallel using the existing event contract.
- T004 can also proceed in parallel with the server tasks; the client does not
  depend on server implementation details.
- T002 and T003 modify the same server file and should be completed in order,
  not in parallel.
- No separate story phases exist to parallelize.

## Implementation Strategy

1. **MVP**: Complete User Story 1: write the tests, implement server-side state
   and validation, connect the Vue/Phaser UI, and align the authoritative
   business specification.
2. **Verify**: Run the Python suite and validate synchronization and rejected
   requests in two browser clients using `quickstart.md`.
3. Keep the existing event-driven architecture and dependencies; do not add
   persistence, new services, or a frontend build system.
