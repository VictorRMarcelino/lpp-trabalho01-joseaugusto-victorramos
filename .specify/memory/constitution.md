<!--
Sync Impact Report
Version change: not defined -> 1.0.0 (initial constitution)
Modified principles:
- Principle slot 1 -> I. Specification Fidelity
- Principle slot 2 -> II. Architectural Continuity
- Principle slot 3 -> III. Approved Technology Stack
- Principle slot 4 -> IV. Server-Authoritative Event Model
- Principle slot 5 -> V. Verifiable Business Rules
Added sections: Additional Constraints; Development Workflow
Removed sections: None
Follow-up TODOs: Establish the original ratification date; it is not available in
the repository history or current project documents.
-->

# Vila em Tempo Real Constitution

## Core Principles

### I. Specification Fidelity
`docs/especificacao.md` is the authoritative source for business rules, event contracts,
and expected behavior. Implementations MUST preserve its defined values, transitions,
and audience for each event. A requirement that is missing or contradictory MUST be
clarified in the specification before implementation; code MUST NOT silently establish
a new business rule.

### II. Architectural Continuity
Before changing or adding functionality, developers MUST inspect the relevant existing
code and follow its established design, architecture, organization, and implementation
patterns. The existing architecture MUST NOT be replaced or reorganized without express
authorization. This prevents feature work from introducing incompatible patterns or
unrequested architectural changes.

### III. Approved Technology Stack
The project MUST use its established Vue, Python, JavaScript, Phaser 3, and Tiled
technologies for their existing responsibilities. New functionality MUST integrate
with the current use of Vue for the interface, Python for the server, JavaScript for
client behavior, Phaser 3 for the game scene, and Tiled for the map. A technology
substitution or architectural addition requires express authorization.

### IV. Server-Authoritative Event Model
The Python server MUST remain the authority for shared game state and business-rule
validation. Clients MUST request actions through the established event flow and render
state received from the server; they MUST NOT independently commit shared state.
Broadcasts and requester-only refusals MUST follow the audiences defined in the
specification. This preserves consistent results for all connected players.

### V. Verifiable Business Rules
Changes to business logic MUST be checked against the specification's scenarios and
event/state transitions. Tests or equivalent reproducible checks MUST cover changed
behavior, including relevant rejection and concurrent-request cases. Review MUST
verify exact values, timing, worker limits, and event outcomes rather than relying on
visual appearance alone.

## Additional Constraints

- The construction cost is 50 flour sacks and construction takes 8 seconds.
- The mill produces 10 flour sacks every 5 seconds. Each completed building produces
  2 loaves every 5 seconds, as specified for the village.
- No more than 2 bakers may be active at once. Processing takes 5 seconds per 2 loaves.
- Construction completion MUST turn the worksite into a functional building and
  release its worker. Bread that is not processed in time loses its value.
- The server MUST stop automatic production and reject new construction after the
  village is closed, as required by the specification.
- The Socket.IO event names, state changes, and recipient scope MUST remain consistent
  with the event table and scenarios in `docs/especificacao.md`.
- When a specification detail cannot be reconciled with existing behavior, the
  specification MUST be clarified; implementation MUST NOT guess.

## Development Workflow

- Before implementation, identify the relevant specification rules, existing code
  paths, and established patterns.
- Keep each change within the requested scope. Do not modify unrelated application
  behavior or introduce dependencies and architecture changes without express
  authorization.
- For each behavior change, verify the related specified scenarios and the affected
  event contracts. Report any checks that cannot be run.
- During review, confirm compliance with this constitution and `docs/especificacao.md`.
  A change that conflicts with either MUST be revised or explicitly authorized through
  the applicable amendment process.

## Governance

This constitution governs development practices and MUST be applied together with
`docs/especificacao.md`, which defines the village's business rules. Amendments require
express approval, a documented change to this file, and review of their effect on the
specification, architecture, and existing behavior. Changes to business rules also
require an approved corresponding specification update.

Versioning follows semantic versioning: MAJOR for incompatible changes to principles
or governance, MINOR for new principles or materially expanded requirements, and PATCH
for clarifications or non-semantic wording changes. The version and amendment date
MUST be updated with each approved amendment.

Every implementation review MUST check the applicable principles, specification
requirements, architecture continuity, and verification evidence. Non-compliant
changes MUST NOT be accepted without explicit authorization and a documented
constitution amendment where required.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date unavailable | **Last Amended**: 2026-10-28
