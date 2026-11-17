# T012 — Compliance Release

**Stage:** R3  |  **Status:** BLOCKED  |  **Dependencies:** T002-T011 + qualified experts  |  **As of:** 2026-11-17

## Objective and scope
Obtain qualified review for Vietnam online game/service classification, rights, privacy, age/content and payments; implement release gate checklists.

## Before work
Read `AGENTS.md`, `docs/agent/PROJECT_STATE.md`, `docs/agent/CURRENT_TASK.md`, this task and the linked architecture/spec. Check git status and run baseline unit tests. Stop if a rights/legal/payment action lacks explicit authorization.

## First exact action
```
read docs/operations/LEGAL_RIGHTS_RELEASE_GATES.md
```

## Implementation rules
Preserve existing API contracts, event logs and content rights. Add both normal and negative tests, handle network failure/retry/idempotency, and do not silently activate paid external calls. For any infrastructure change record deployment architecture, secrets, monitoring and rollback impact. For model work, preserve prompt/model/dataset licensing and benchmarks.

## Definition of done / acceptance
All applicable permits/agreements recorded; external reviewer signoff evidence present; public release blocked otherwise.

## Evidence checklist
- [ ] Code or research artifact checked into documented path.
- [ ] Relevant requirement IDs in `FUNCTIONAL_SPEC.md` updated from source table.
- [ ] Exact tests run and results copied into `SESSION_LOG.md`.
- [ ] Negative cases, edge conditions and security/rights checks covered.
- [ ] `PROJECT_STATE.md`, `CURRENT_TASK.md`, `BACKLOG.md` and owner decision/ADR updated.
- [ ] Clear next task and a reproducible first command recorded.

## Known risks and out-of-scope
Public production access is blocked until rights, privacy, financial and any game/service licensing obligations are reviewed. Current proof-of-concept must not be mistaken for a cleared commercial product.
