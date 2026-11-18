# PROJECT_STATE — Canonical project memory

**Updated:** 2026-11-18 | **Stage:** R1 complete (`T000`–`T005` DONE); R2 next (`T006` Narrative AI provider adapters & schema verifier) | **Task completed:** T005 Player lifecycle, offline/resume/background plan

Evidence: [ONBOARDING_AUDIT_20261117.md](ONBOARDING_AUDIT_20261117.md), [T001_FLUTTER_BOOTSTRAP.md](../tasks/T001_FLUTTER_BOOTSTRAP.md), [T002_RIGHTS_PROVENANCE.md](../tasks/T002_RIGHTS_PROVENANCE.md), [T003_AUTH_POSTGRES.md](../tasks/T003_AUTH_POSTGRES.md), [T004_SECURE_MEDIA.md](../tasks/T004_SECURE_MEDIA.md), [T005_PLAYER_LIFECYCLE.md](../tasks/T005_PLAYER_LIFECYCLE.md), and [SESSION_LOG.md](SESSION_LOG.md).

## DONE — verified locally, not production acceptance
- FastAPI catalog/work/rights/auth/me/admin/playback/downloads/media/run/choice/progress/history/restore API and loopback HTTP/static delivery.
- Original demo graph: 11 scenes, all authored branches reachable, exactly 3 reachable endings.
- **T005 Player Lifecycle, Progress Resume, Speed/Sleep/Seek Controls & Offline Leases (`backend/audioverse/migrations.py`, `backend/audioverse/storage.py`, `backend/audioverse/media.py`, `backend/audioverse/main.py`, `web/app.js`, `mobile/lib/*`):**
  - Migration `004_playback_progress_library_and_offline_leases` (`position_ms` & `playback_speed` on `runs`, `user_library` follow table, `offline_leases` table).
  - Playback progress write-back (`POST /api/v1/runs/{run_id}/progress`), continue-listening resume (`GET /api/v1/me/continue-listening`), library follow toggles (`POST /api/v1/me/library/{work_id}`, `GET /api/v1/me/library`), and license-scoped offline lease creation/validation (`POST /api/v1/downloads/leases`, `GET /api/v1/downloads/leases/{lease_id}/validate`) enforcing `offline` rights, entitlement status, storage quota (`OFFLINE_STORAGE_QUOTA_EXCEEDED`), and lease expiry (`OFFLINE_LEASE_EXPIRED`) (`CAT-07`, `CAT-08`, `LIB-01`, `LIB-02`, `PLY-05`–`PLY-08`, `PLY-11`, `PLY-13`, `PLY-14`, `PLY-18`, `INT-12`).
  - Flutter `StoryScreen` (`WidgetsBindingObserver` background pause write-back, automatic run/position/speed resume via `continueListening()`, `-10s`/`+10s` seek clamped to `[Duration.zero, duration]`, `0.8x`–`2.0x` playback speed selector, sleep timer, audio focus interruption pause/resume, offline lease download & expiry validation).
  - Fixed `web/app.js` audit finding `A08` (`render(current, true)` preserves status messages on transport failure, retains pending `idempotency_key`, and auto-refreshes run state on HTTP `409`).
- **T004 Authenticated Media Streaming & Signed Delivery (`backend/audioverse/media.py`, `backend/audioverse/migrations.py`, `backend/audioverse/main.py`):**
  - Private `media_objects` registry (`asset_id`, `sha256`, `byte_size`, `rights_grant_version`, `cache_epoch`), `user_entitlements` (`allow_stream`, `allow_offline`, `expires_at`, `revoked_at`), and redacted `media_delivery_logs`.
  - Short-lived HMAC-SHA256 signed media authorization (`POST /api/v1/playback/authorize`) and delivery (`GET /api/v1/media/{asset_id}?token=...`) with HTTP Range (`206 Partial Content`) support, private cache headers (`Cache-Control: private, max-age=..., must-revalidate`), and staff cache invalidation (`POST /api/v1/admin/media/{asset_id}/invalidate`) (`PLY-10`, `PLY-15`, `SEC-09`).
  - Revalidates token TTL, signature, actor binding, active device session (honoring logout immediately), entitlement status, `cache_epoch`, rights grant version, and live rights/quarantine/takedown status at delivery time.
- **T003 Authentication, RBAC, Migrations, Edition Pinning & Tamper-Evident Storage (`backend/audioverse/auth.py`, `backend/audioverse/migrations.py`, `backend/audioverse/storage.py`):**
  - Scrypt password hashing, HMAC-SHA256 signed Bearer tokens bound to revocable `device_sessions`, token rotation, idempotent guest-to-account migration, personal data export/deletion, RBAC with hash-chained `security_audit_log`, DB `BEFORE UPDATE/DELETE` immutability triggers on `events` and `security_audit_log`, `edition_id` pinning (`INT-08`), `story_snapshots`, deterministic event replay recovery (`INT-18`), and PostgreSQL target DDL with Row-Level Security (`RLS`).
- **T002 Canonical Rights Provenance & Maker-Checker Policy Engine (`backend/audioverse/rights.py`, `backend/audioverse/content.py`, `content/licenses/demo_license.json`):**
  - Typed `RightsGrant`, `ContractEvidence`, `ChainOfTitle`, `ReviewAuditEntry`, `AssetLicense`, and `RightsManifest` models enforcing separate `stream`, `offline`, `derivative`, `tts`, `voice_clone`, and `training` permissions (`RGT-01`..`RGT-14`), maker-checker workflow, prohibited public scrape URL guard, 60/30/7-day renewal warnings, SHA-256 verification across all 11 demo MP3s, dispute holds, and takedown freezes.
- **T001 Flutter Bootstrap & Android Emulator E2E Validation:**
  - Flutter `3.50.0` (Dart `3.14.0`) at `D:\flutter` and Android SDK (`platforms;android-35/36`, `build-tools;35.0.0/36.0.0`, `ndk;28.2.13676358`, `cmake;3.22.1`, `emulator` `37.2.13.0`, `platform-tools` `37.0.1`) at `D:\Android\Sdk`.
  - `flutter analyze` (**0 issues**), `flutter test` (**7/7 widget tests passed**), `flutter build apk --debug`, and live headless Android 15 (API 35) emulator E2E verification all passed.
- Windows Python 3.13.9 isolated `.venv`: **35 backend tests passed, 1 Starlette/httpx deprecation warning**. Repository check: **11 scenes, 182 requirements**. Compilation, full configured Ruff, JavaScript syntax, and pip dependency consistency pass.

## PARTIAL — code or limited checks, acceptance incomplete
- Browser experience: HTML/JS/CSS and HTTP path verified, `A08` error-preservation and `409` refresh fixed in `web/app.js`, plus live browser verification of `http://127.0.0.1:8765/` and Flutter Web preview `http://127.0.0.1:8766/`.
- Mobile iOS & physical device background media: `mobile/ios` wrapper generated, but iOS build/Simulator execution requires macOS/Xcode (unrun on Windows). Physical lockscreen/Bluetooth headset controls on real devices remain part of device release QA (`PLY-03`, `PLY-17`).

## PLANNED — not implemented
- Narrative planner/writer/validator, provider adapters, generation queue, budgets/cost ledger, production TTS or fine-tuning (`T006` next, `T007`, `T010`, `T015`).
- Creator/reviewer web CMS and content versioning/branching editor (`T008`, `T009`).
- Payments, store receipts/entitlements, royalty settlement, analytics and commercial operations (`T011`).

## BLOCKED
- iOS native compilation/Simulator validation: requires macOS + Xcode hardware environment.
- Public/commercial launch (`T011`–`T014`): expert Vietnam classification/privacy review, documented per-asset rights/voice approval, security/auth/media foundation, mobile QA and store/payment gates remain unmet.

## Git / next task
- Active branch: `main` (tracking `origin/main`), containing all verified `T000`–`T005` work.
- Next: **T006 — Narrative AI provider adapters & schema verifier** (`READY`).
