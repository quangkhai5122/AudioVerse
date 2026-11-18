# PROJECT_STATE — Canonical project memory

**Updated:** 2026-11-18 | **Stage:** R1 in progress (T001 Android verified; R1 security/rights pending) | **Task completed:** T001 Flutter Bootstrap & Device Validation

Evidence: [ONBOARDING_AUDIT_20261117.md](ONBOARDING_AUDIT_20261117.md), [T001_FLUTTER_BOOTSTRAP.md](../tasks/T001_FLUTTER_BOOTSTRAP.md), and [SESSION_LOG.md](SESSION_LOG.md).

## DONE — verified locally, not production acceptance
- FastAPI catalog/work/run/choice/history API and loopback HTTP/static delivery.
- Original demo graph: 11 scenes, all authored branches reachable, exactly 3 reachable endings.
- Deterministic flag/precondition transitions; SQLite transactional run/event writes; choice idempotency, stale-version rejection, malformed-input rejection and demo actor scoping.
- Illustrative rights action checks deny absent/disabled grants, voice_clone and training. No authenticated legal review is implied.
- All 11 packaged MP3s return HTTP 200; sample byte range returns 206.
- Windows Python 3.13.9 isolated `.venv`: **17 tests passed, 1 Starlette/httpx deprecation warning**. Repository check: **11 scenes, 182 requirements**. Compilation, full configured Ruff, JavaScript syntax, HTTP/11-MP3 smoke and pip dependency consistency pass.
- **T001 Flutter Bootstrap & Android Emulator E2E Validation:**
  - Installed Flutter `3.50.0` (Dart `3.14.0`) at `D:\flutter` and Android SDK (`platforms;android-35/36`, `build-tools;35.0.0/36.0.0`, `ndk;28.2.13676358`, `cmake;3.22.1`, `emulator` `37.2.13.0`, `platform-tools` `37.0.1`) at `D:\Android\Sdk`.
  - Generated native `mobile/android` and `mobile/ios` wrappers and `mobile/pubspec.lock`; configured debug-only cleartext HTTP (`10.0.2.2`, `127.0.0.1`, `localhost`) via `mobile/android/app/src/debug/res/xml/network_security_config.xml` without weakening release manifests.
  - Fixed starter `CatalogScreen` `setState` returning `Future` bug, implemented `SceneAudioController` abstraction, committed-choice before audio-load state update with `"Thử tải lại âm thanh"` recovery, pending `idempotency_key` retention on transport errors, and automatic `409 Conflict` state refresh via `GET /api/v1/runs/{run_id}`.
  - `flutter analyze` (**0 issues**), `flutter test` (**6/6 widget tests passed**), `flutter build apk --debug` (`app-debug.apk` built), and live headless Android 15 (API 35, `audioverse_api35`) emulator E2E verification (offline error -> retry -> catalog -> `s0 -> s1 -> s3 -> s4 -> s8` + MP3 streaming + SQLite verification) all passed.

## PARTIAL — code or limited checks, acceptance incomplete
- Browser experience: HTML/JS/CSS and HTTP path verified; no real browser/audio listening or automated browser E2E. Web `choose()` catch block still calls `render(current)` which can overwrite error text.
- Mobile iOS & background lifecycle: `mobile/ios` wrapper generated, but iOS build/Simulator execution requires macOS/Xcode (unrun on Windows). Persistent cross-restart run/position storage, background audio (`audio_service`), lockscreen controls, and offline downloads remain deferred to `T005`.
- Rights JSON checks permissions only; no expiry, territory, evidence validation, authenticated reviewer or revocation workflow (`T002` next).
- SQLite event history is append-only by application convention. No DB UPDATE/DELETE guard, tamper evidence, replay restore or immutable edition hash is implemented (`T003`/`T009`).
- Ubuntu/Python 3.11 CI verified for backend; Flutter CI job is not yet added to `.github/workflows/ci.yml`.

## PLANNED — not implemented
- Canonical content/rights provenance schema, reviewer/CMS/creator ingestion and licensed human recordings (`T002`, `T008`).
- Real accounts/auth/RBAC; Postgres/migrations; private media authorization; rate limiting, backups and production privacy/security controls (`T003`, `T004`).
- Fixed-audio edition/library management, search, background/offline playback, position sync, passive default route and process/network recovery (`T005`, `T009`).
- Narrative planner/writer/validator, provider adapters, generation queue, budgets/cost ledger, production TTS or fine-tuning (`T006`, `T007`, `T010`, `T015`).
- Payments, store receipts/entitlements, royalty settlement, analytics and commercial operations (`T011`).

## BLOCKED
- iOS native compilation/Simulator validation: requires macOS + Xcode hardware environment.
- Public/commercial launch (`T011`–`T014`): expert Vietnam classification/privacy review, documented per-asset rights/voice approval, security/auth/media foundation, mobile QA and store/payment gates remain unmet.

## Important verified limitations
- `X-Demo-Actor` is spoofable and defaults to a shared actor; scoping tests are not real authentication.
- Loopback is the launcher default, **not an enforced bind restriction**: `AUDIOVERSE_HOST` or a direct ASGI launcher can expose the demo. Never use a LAN/public bind.
- Story runs pin only `story_id`, not immutable edition/version; editing the graph can invalidate existing runs.
- Mobile foreground recovery is now verified for in-memory runs (`T001`), but persistent across-process-death run/key/position recovery remains scoped to `T005`.

## Git / next task
- Active branch: `main` (tracking `origin/main`), containing all verified `T000` and `T001` commits. Under owner policy updated 2026-11-18, ordinary scoped work is developed directly on `main` and pushed to `origin/main` when verification checks pass (no separate branch per milestone).
- Next: **T002 — Content rights schema, contract and evidence review design** (`READY`). Follow with `T003` (Postgres, migrations, user auth and tenant isolation) and `T004` (Authenticated media streaming).
