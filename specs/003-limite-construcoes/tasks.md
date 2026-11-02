# Tasks: Limite de construções

**Input**: Design documents from `specs/003-limite-construcoes/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/socketio-events.md`

**Tests**: Include server tests because the project constitution requires reproducible checks for business-rule changes and the plan specifies `unittest` coverage.

**Organization**: Tasks are grouped by user story so the limit can be implemented and validated as an independent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with another task without editing the same files or depending on incomplete work
- **[Story]**: User story addressed by the task
- Every task specifies the file it creates, updates, or uses for validation

## Phase 1: Setup

**Purpose**: Project initialization and shared infrastructure.

No setup tasks are needed: the Python server, Socket.IO client, and `unittest`
test infrastructure already exist.

---

## Phase 2: Foundational

**Purpose**: Blocking prerequisites for user-story implementation.

No foundational changes are needed. The feature uses the existing in-memory
village state and refusal event.

---

## Phase 3: User Story 1 - Construir sem ultrapassar o limite (Priority: P1) 🎯 MVP

**Goal**: Accept construction requests only while fewer than six builds are
completed or in progress; otherwise notify only the requester without changing
the village or its resources.

**Independent Test**: Fill all six slots using any combination of completed
buildings and active works, request another, and confirm that it is refused
without state changes and that the requester sees the limit warning. Also
submit two requests for the last slot and confirm that only one is accepted.

### Tests for User Story 1

- [X] T001 [US1] Add `unittest` cases in `tests/test_server_construction_limit.py` for accepting the sixth build, refusing a seventh with six completed builds, refusing when five are completed and one is in progress, preserving counters/workers/coins on refusal, and concurrent requests competing for the last slot; assert `operacao.recusada` is directed only to the refused requester.

### Implementation for User Story 1

- [X] T002 [US1] Update the `construir` handler in `server.py` to validate `estado["concluidas"] + estado["em_obra"] < 6` before changing coins, workers, or work count; refuse a full village through `operacao.recusada` with cause `construcao.solicitada` and a reason stating that the construction limit has been reached, without adding an `await` between validation and reservation.
- [X] T003 [US1] Run `python -m unittest discover -s tests` and confirm the construction-limit cases in `tests/test_server_construction_limit.py` and the existing server tests pass.

**Checkpoint**: The server never reserves a seventh slot, including under
concurrent requests, and a refused requester receives the existing warning.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validate the existing client refusal flow end to end.

- [X] T004 Validate the full-capacity refusal in two browser clients using `specs/003-limite-construcoes/quickstart.md` and confirm `client/index.html` shows the reason only to the requester without replacing a building.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No tasks; the existing project structure is reused.
- **Foundational (Phase 2)**: No tasks; existing state and events provide the prerequisites.
- **User Story 1 (Phase 3)**: Independent MVP; complete its tests, implementation, and automated validation in order.
- **Polish (Phase 4)**: Depends on User Story 1 implementation; validates the existing browser flow.

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories.

### Within User Story 1

- T001 adds the behavioral tests first.
- T002 implements the server-side guard after T001.
- T003 runs automated validation after T002.
- T004 performs the browser validation after T003.

### Parallel Opportunities

- No tasks are marked parallel: the test-first implementation and validation steps depend on the preceding task, and the feature changes only one server handler and one new test file.

---

## Parallel Example: User Story 1

There are no safe parallel task groups for this story. Complete T001 through
T004 in dependency order.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Add the limit, refusal, preservation, and concurrent-request tests in
   `tests/test_server_construction_limit.py`.
2. Add the authoritative total-count check to `server.py`.
3. Run the full `unittest` suite and validate the requester-only warning in the
   existing client using `specs/003-limite-construcoes/quickstart.md`.
4. Stop after the P1 user story; no other user stories are specified.
