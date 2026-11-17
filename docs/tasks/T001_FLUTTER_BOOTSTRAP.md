# T001 — Flutter Bootstrap

**Stage:** R1  |  **Status:** PLANNED; local execution BLOCKED (toolchain)  |  **Dependencies:** Flutter/Dart + Android SDK/emulator  |  **As of:** 2026-11-17

T000 onboarding is complete; the owner deferred T001 implementation to a later session. No native scaffolding, Flutter dependency resolution, analyze/test/build or device QA has run. See CURRENT_TASK and ONBOARDING_AUDIT_20261117 for evidence.

## Objective and scope
Generate native Android/iOS wrappers, run flutter analyze and implement at least one widget test; verify MP3 playback, choice transition and emulator network in debug-only cleartext.

## Before work
Read `AGENTS.md`, `docs/agent/PROJECT_STATE.md`, `docs/agent/CURRENT_TASK.md`, this task and the linked architecture/spec. Check git status and run baseline unit tests. Stop if a rights/legal/payment action lacks explicit authorization.

## First exact action
```
Get-Command flutter,dart,adb -ErrorAction SilentlyContinue
```

Resolve missing SDKs first. Then from mobile run `flutter doctor -v`, `flutter create --platforms=android,ios --project-name audioverse .`, `flutter pub get`, `flutter analyze`, `flutter test` and `flutter build apk --debug` sequentially. Preserve existing sources when generating wrappers. iOS validation needs macOS/Xcode and remains unrun on Windows.

## Implementation rules
Preserve existing API contracts, event logs and content rights. Add both normal and negative tests, handle network failure/retry/idempotency, and do not silently activate paid external calls. For any infrastructure change record deployment architecture, secrets, monitoring and rollback impact. For model work, preserve prompt/model/dataset licensing and benchmarks.

## Definition of done / acceptance
Flutter analyze/widget test and Android emulator manual happy+error path pass; native project committed with no insecure production network config.

The existing widget smoke starts a real API request and has not run; add a fake API. Cover uncertain duplicate submits, 409 refresh and a committed choice followed by failed `_load` audio leaving stale `_run`. Record emulator evidence separately from static analysis; broader lifecycle/background/offline remains T005.

## Evidence checklist
- [ ] Code or research artifact checked into documented path.
- [ ] Relevant requirement IDs in `FUNCTIONAL_SPEC.md` updated from source table.
- [ ] Exact tests run and results copied into `SESSION_LOG.md`.
- [ ] Negative cases, edge conditions and security/rights checks covered.
- [ ] `PROJECT_STATE.md`, `CURRENT_TASK.md`, `BACKLOG.md` and owner decision/ADR updated.
- [ ] Clear next task and a reproducible first command recorded.

## Known risks and out-of-scope
Public production access is blocked until rights, privacy, financial and any game/service licensing obligations are reviewed. Current proof-of-concept must not be mistaken for a cleared commercial product.
