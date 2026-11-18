# CURRENT_TASK — one next engineering packet

**Next:** T005 — Player lifecycle, offline/resume/background plan
**Implementation:** READY, not started
**Previous:** T004 — Authenticated media streaming and signed delivery DONE on `main`
**Authorization:** ordinary local development/commit/push on `main` is pre-authorized; deployment/store/content publication is not.

## Exact next commands (PowerShell, repository root)

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=".venv\pytest_tmp"; Remove-Item -Recurse -Force ".venv\pytest_tmp" -ErrorAction SilentlyContinue
Push-Location mobile; D:\flutter\bin\flutter.bat analyze; D:\flutter\bin\flutter.bat test; Pop-Location
```

Read `AGENTS.md`, `docs/agent/PROJECT_STATE.md`, `docs/agent/BACKLOG.md`, latest `docs/agent/SESSION_LOG.md`, `docs/tasks/T005_PLAYER_LIFECYCLE.md`, and `docs/engineering/FLUTTER_CLIENT.md` before editing.

## Objective & Scope for T005
- Implement playback progress persistence and resume (`POST /api/v1/runs/{run_id}/progress` / `GET /api/v1/me/continue-listening`, `PLY-08`, `LIB-02`, `INT-12`), playback speed (`0.8x`–`2.0x`, `PLY-05`), sleep timer (`PLY-06`), seek increments (`PLY-07`), audio focus interruption handling (`PLY-13`), signed playback URL resolution & license-scoped offline download manager (`PLY-10`, `PLY-11`) in the Flutter client and backend.
- Fix the remaining `web/app.js` error-overwrite issue (`A08`) and add Flutter widget & backend tests for pause/interrupt/network/offline/license-expiry and position resume.

## Acceptance criteria
- [ ] Playback position and active run persist across pause/background/app restart and sync with backend (`PLY-08`, `INT-12`, `LIB-02`).
- [ ] Player supports speed control (`0.8x`–`2.0x`, `PLY-05`), sleep timer (`PLY-06`), seek forward/backward clamped to duration (`PLY-07`), and audio focus interruption pause/resume (`PLY-13`).
- [ ] Offline download manager verifies `offline` signed media grant, checks license expiry before offline playback (`PLY-10`, `PLY-11`), and blocks expired/revoked offline access.
- [ ] Relevant `PLY-*`, `LIB-*`, and `INT-*` requirement statuses updated in `docs/product/requirements.psv` and regenerated in `docs/product/FUNCTIONAL_SPEC.md`.
- [ ] Backend tests, repository check, Ruff, and Flutter `analyze`/`test` remain green; commit and push directly to `origin/main`.
