# T005 — Player Lifecycle

**Stage:** R1  |  **Status:** DONE  |  **Dependencies:** T001,T004  |  **As of:** 2026-11-18

## Objective and scope
Finish background media session, headset/lockscreen, resume progress, offline authorized downloads, network recovery and accessibility.

## Before work
Read `AGENTS.md`, `docs/agent/PROJECT_STATE.md`, `docs/agent/CURRENT_TASK.md`, this task and the linked architecture/spec. Check git status and run baseline unit tests. Stop if a rights/legal/payment action lacks explicit authorization.

## First exact action
```
cd mobile && flutter analyze
```

## Implementation rules
Preserve existing API contracts, event logs and content rights. Add both normal and negative tests, handle network failure/retry/idempotency, and do not silently activate paid external calls. For any infrastructure change record deployment architecture, secrets, monitoring and rollback impact. For model work, preserve prompt/model/dataset licensing and benchmarks.

## Definition of done / acceptance
Android and iOS tests for pause/call/network/offline/license expiry and position resume; no playback corruption.

## Evidence checklist
- [x] Code or research artifact checked into documented path (`backend/audioverse/migrations.py`, `backend/audioverse/storage.py`, `backend/audioverse/media.py`, `backend/audioverse/main.py`, `backend/tests/test_player_lifecycle.py`, `web/app.js`, `mobile/lib/models/story_models.dart`, `mobile/lib/services/scene_audio_controller.dart`, `mobile/lib/services/api_client.dart`, `mobile/lib/screens/story_screen.dart`, `mobile/test/app_smoke_test.dart`).
- [x] Relevant requirement IDs (`CAT-07`, `CAT-08`, `LIB-01`, `LIB-02`, `PLY-05`, `PLY-06`, `PLY-07`, `PLY-08`, `PLY-11`, `PLY-13`, `PLY-14`, `PLY-18`, `INT-12`) in `FUNCTIONAL_SPEC.md` updated from source table (`docs/product/requirements.psv`).
- [x] Exact tests run and results copied into `SESSION_LOG.md` (`35 passed` in `pytest`, `7 passed` in `flutter test`, `0` issues in `flutter analyze`).
- [x] Negative cases, edge conditions and security/rights checks covered (seek boundary clamping, audio focus interruption resume, offline storage quota `422 OFFLINE_STORAGE_QUOTA_EXCEEDED`, expired offline lease `403 OFFLINE_LEASE_EXPIRED`, revoked entitlement `403 ENTITLEMENT_REQUIRED`, `web/app.js` `A08` error preservation & `409` refresh).
- [x] `PROJECT_STATE.md`, `CURRENT_TASK.md`, `BACKLOG.md` and owner decision/ADR updated.
- [x] Clear next task (`T006 — Narrative AI provider adapters & schema verifier`) and a reproducible first command recorded.

## Known risks and out-of-scope
Public production access is blocked until rights, privacy, financial and any game/service licensing obligations are reviewed. Current proof-of-concept must not be mistaken for a cleared commercial product.
