# CURRENT_TASK — one next engineering packet

**Next:** T001 — Flutter Bootstrap & Device Validation
**Implementation:** PLANNED, not started
**Local execution:** BLOCKED until Flutter/Dart + Android SDK/emulator are available
**Previous:** T000 onboarding audit DONE (re-verified 2026-11-18); see ONBOARDING_AUDIT_20261117.md
**Authorization:** ordinary local development/commit/push is pre-authorized; deployment/store/content publication is not.

## Exact next commands (PowerShell, repository root)

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=".venv\pytest_tmp"; Remove-Item -Recurse -Force ".venv\pytest_tmp" -ErrorAction SilentlyContinue
Get-Command flutter,dart,adb -ErrorAction SilentlyContinue
```

Read AGENTS/state/backlog/latest log and T001 before editing. If no Flutter SDK is available, obtain/verify a local toolchain during T001 and record exact versions; do not claim native validation. Base `python` (`D:\miniconda3\python.exe` or Windows Store alias) lacks FastAPI and `py -3.14` points to a missing interpreter. The ignored `.venv` was created with `D:\miniconda3\python.exe` (3.13.9); use its explicit interpreter path, and pass `-p no:cacheprovider --basetemp=".venv\pytest_tmp"` when running pytest across sandboxed Windows sessions to avoid `WinError 5` on `%TEMP%\pytest-of-*` and `.pytest_cache`.

After the SDK is available, from `mobile` run these sequentially, checking each result:

```powershell
flutter doctor -v
flutter create --platforms=android,ios --project-name audioverse .
flutter pub get
flutter analyze
flutter test
flutter build apk --debug
```

Inspect generated changes to preserve existing lib/test/pubspec files. Start backend at loopback; Android emulator uses `--dart-define=API_BASE=http://10.0.2.2:8765`. INTERNET and cleartext exceptions must be debug-only. Never expose the backend on LAN for physical-device testing. iOS native checks require a separate macOS/Xcode environment and must remain explicitly unrun on Windows.

## Acceptance criteria
- [ ] Record SDK/tool/device versions; Flutter analyze, mocked widget tests and Android debug build pass.
- [ ] Android emulator shows catalog, plays demo MP3, traverses a branch and reaches an ending; network/API/audio failures are recorded and handled within foreground scope.
- [ ] Existing smoke test is made deterministic with a fake API; merely having the widget file is not passing evidence.
- [ ] Check committed-choice/audio-failure recovery and 409 refresh; retain pending idempotency key when retrying an uncertain submission. Record any work explicitly deferred to T005.
- [ ] Debug HTTP config does not weaken release manifests; no remote AI or public exposure.
- [ ] Backend tests/repository check/Ruff remain green; update task/state/backlog/log with exact execution evidence.

After T001, follow T002 rights provenance, then T003 security/auth and persistence. T002 is independently available for local design if the toolchain genuinely cannot be restored; record any task-selection change explicitly.
