# T016 — Creator Marketplace

**Stage:** R5  |  **Status:** DEFERRED  |  **Dependencies:** T008,T012  |  **As of:** 2026-11-18

## Objective and scope
Consider creator self-service publishing, moderation, reporting/appeals, royalty payouts and content discovery.

## Before work
Read `AGENTS.md`, `docs/agent/PROJECT_STATE.md`, `docs/agent/CURRENT_TASK.md`, this task and the linked architecture/spec. Check git status and run baseline unit tests. Stop if a rights/legal/payment action lacks explicit authorization.

## First exact action
```
read docs/operations/CONTENT_SAFETY.md
```

## Implementation rules
Preserve existing API contracts, event logs and content rights. Add both normal and negative tests, handle network failure/retry/idempotency, and do not silently activate paid external calls. For any infrastructure change record deployment architecture, secrets, monitoring and rollback impact. For model work, preserve prompt/model/dataset licensing and benchmarks.

## Definition of done / acceptance
Platform abuse and copyright report flow tested; legal/financial obligations and content moderation staffed.

## Evidence checklist
- [ ] Code or research artifact checked into documented path.
- [ ] Relevant requirement IDs in `FUNCTIONAL_SPEC.md` updated from source table.
- [ ] Exact tests run and results copied into `SESSION_LOG.md`.
- [ ] Negative cases, edge conditions and security/rights checks covered.
- [ ] `PROJECT_STATE.md`, `CURRENT_TASK.md`, `BACKLOG.md` and owner decision/ADR updated.
- [ ] Clear next task and a reproducible first command recorded.

## Known risks and out-of-scope
Public production access is blocked until rights, privacy, financial and any game/service licensing obligations are reviewed. Current proof-of-concept must not be mistaken for a cleared commercial product.
