# PROJECT_STATE — Canonical project memory

**Updated:** 2026-11-18 | **Stage:** R1 in progress (`T000`–`T004` DONE; `T005` Player Lifecycle next) | **Task completed:** T004 Authenticated media streaming and signed delivery

Evidence: [ONBOARDING_AUDIT_20261117.md](ONBOARDING_AUDIT_20261117.md), [T001_FLUTTER_BOOTSTRAP.md](../tasks/T001_FLUTTER_BOOTSTRAP.md), [T002_RIGHTS_PROVENANCE.md](../tasks/T002_RIGHTS_PROVENANCE.md), [T003_AUTH_POSTGRES.md](../tasks/T003_AUTH_POSTGRES.md), [T004_SECURE_MEDIA.md](../tasks/T004_SECURE_MEDIA.md), and [SESSION_LOG.md](SESSION_LOG.md).

## DONE — verified locally, not production acceptance
- FastAPI catalog/work/rights/auth/me/admin/playback/media/run/choice/history/restore API and loopback HTTP/static delivery.
- Original demo graph: 11 scenes, all authored branches reachable, exactly 3 reachable endings.
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
  - `flutter analyze` (**0 issues**), `flutter test` (**6/6 widget tests passed**), `flutter build apk --debug`, and live headless Android 15 (API 35) emulator E2E verification all passed.
- Windows Python 3.13.9 isolated `.venv`: **33 backend tests passed, 1 Starlette/httpx deprecation warning**. Repository check: **11 scenes, 182 requirements**. Compilation, full configured Ruff, JavaScript syntax, and pip dependency consistency pass.

## PARTIAL — code or limited checks, acceptance incomplete
- Browser experience: HTML/JS/CSS and HTTP path verified, plus live browser verification of `http://127.0.0.1:8765/` and Flutter Web preview `http://127.0.0.1:8766/`; Web `choose()` catch block in `web/app.js` still calls `render(current)` which can overwrite error text.
- Mobile iOS & background lifecycle: `mobile/ios` wrapper generated, but iOS build/Simulator execution requires macOS/Xcode (unrun on Windows). Persistent cross-restart run/position storage, background audio (`audio_service`), lockscreen controls, and offline downloads are next in `T005`.

## PLANNED — not implemented
- Player lifecycle, background audio, position resume, playback speed/sleep timer, and authorized offline downloads (`T005` next).
- Narrative planner/writer/validator, provider adapters, generation queue, budgets/cost ledger, production TTS or fine-tuning (`T006`, `T007`, `T010`, `T015`).
- Creator/reviewer web CMS and content versioning/branching editor (`T008`, `T009`).
- Payments, store receipts/entitlements, royalty settlement, analytics and commercial operations (`T011`).

## BLOCKED
- iOS native compilation/Simulator validation: requires macOS + Xcode hardware environment.
- Public/commercial launch (`T011`–`T014`): expert Vietnam classification/privacy review, documented per-asset rights/voice approval, security/auth/media foundation, mobile QA and store/payment gates remain unmet.

## Git / next task
- Active branch: `main` (tracking `origin/main`), containing all verified `T000`–`T004` work.
- Next: **T005 — Player lifecycle, offline/resume/background plan** (`READY`).
