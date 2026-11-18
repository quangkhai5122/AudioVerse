# PROJECT_STATE — Canonical project memory

**Updated:** 2026-11-18 | **Stage:** R1 in progress (`T000`–`T003` DONE; `T004` Secure Media next) | **Task completed:** T003 Postgres, migrations, user auth and tenant isolation design

Evidence: [ONBOARDING_AUDIT_20261117.md](ONBOARDING_AUDIT_20261117.md), [T001_FLUTTER_BOOTSTRAP.md](../tasks/T001_FLUTTER_BOOTSTRAP.md), [T002_RIGHTS_PROVENANCE.md](../tasks/T002_RIGHTS_PROVENANCE.md), [T003_AUTH_POSTGRES.md](../tasks/T003_AUTH_POSTGRES.md), and [SESSION_LOG.md](SESSION_LOG.md).

## DONE — verified locally, not production acceptance
- FastAPI catalog/work/rights/auth/me/admin/run/choice/history/restore API and loopback HTTP/static delivery.
- Original demo graph: 11 scenes, all authored branches reachable, exactly 3 reachable endings.
- **T003 Authentication, RBAC, Migrations, Edition Pinning & Tamper-Evident Storage (`backend/audioverse/auth.py`, `backend/audioverse/migrations.py`, `backend/audioverse/storage.py`):**
  - Scrypt password hashing, HMAC-SHA256 signed Bearer tokens bound to revocable `device_sessions` and `access_jti`, token rotation (`POST /api/v1/auth/refresh`), device revocation (`GET/DELETE /api/v1/me/devices`), idempotent one-time guest-to-account migration (`POST /api/v1/me/migrate-guest`), personal data export (`GET /api/v1/me/export`), and account deletion/anonymization (`DELETE /api/v1/me`) (`ACC-01`..`ACC-07`, `SEC-01`, `SEC-02`, `SEC-07`, `SEC-14`).
  - Role-based access control (`listener`, `creator`, `legal_reviewer`, `rights_officer`, `compliance_admin`) with append-only hash-chained `security_audit_log` recording privilege escalation attempts (`ACC-10`, `SEC-12`).
  - Versioned schema migrations (`schema_migrations`), database-level `BEFORE UPDATE/DELETE` immutability triggers on `events` and `security_audit_log`, immutable story edition pinning (`editions`, `INT-08`), `story_snapshots`, deterministic event replay recovery (`POST /api/v1/runs/{run_id}/restore`, `INT-18`), and PostgreSQL target DDL with Row-Level Security (`RLS`).
- **T002 Canonical Rights Provenance & Maker-Checker Policy Engine (`backend/audioverse/rights.py`, `backend/audioverse/content.py`, `content/licenses/demo_license.json`):**
  - Typed `RightsGrant`, `ContractEvidence`, `ChainOfTitle`, `ReviewAuditEntry`, `AssetLicense`, and `RightsManifest` models enforcing separate `stream`, `offline`, `derivative`, `tts`, `voice_clone`, and `training` permissions (`RGT-01`..`RGT-14`), maker-checker workflow, prohibited public scrape URL guard, 60/30/7-day renewal warnings, SHA-256 verification across all 11 demo MP3s, dispute holds, and takedown freezes.
- **T001 Flutter Bootstrap & Android Emulator E2E Validation:**
  - Flutter `3.50.0` (Dart `3.14.0`) at `D:\flutter` and Android SDK (`platforms;android-35/36`, `build-tools;35.0.0/36.0.0`, `ndk;28.2.13676358`, `cmake;3.22.1`, `emulator` `37.2.13.0`, `platform-tools` `37.0.1`) at `D:\Android\Sdk`.
  - `flutter analyze` (**0 issues**), `flutter test` (**6/6 widget tests passed**), `flutter build apk --debug`, and live headless Android 15 (API 35) emulator E2E verification all passed.
- Windows Python 3.13.9 isolated `.venv`: **30 backend tests passed, 1 Starlette/httpx deprecation warning**. Repository check: **11 scenes, 182 requirements**. Compilation, full configured Ruff, JavaScript syntax, and pip dependency consistency pass.

## PARTIAL — code or limited checks, acceptance incomplete
- Browser experience: HTML/JS/CSS and HTTP path verified, plus live browser verification of `http://127.0.0.1:8765/` and Flutter Web preview `http://127.0.0.1:8766/`; Web `choose()` catch block in `web/app.js` still calls `render(current)` which can overwrite error text.
- Mobile iOS & background lifecycle: `mobile/ios` wrapper generated, but iOS build/Simulator execution requires macOS/Xcode (unrun on Windows). Persistent cross-restart run/position storage, background audio (`audio_service`), lockscreen controls, and offline downloads remain deferred to `T005`.
- Media delivery (`GET /api/v1/audio/{scene_id}.mp3`): enforces `RightsGrant` and `AssetLicense` quarantine/takedown checks (`T002`), but signed short-lived playback URLs and entitlement checks are next in `T004`.

## PLANNED — not implemented
- Authenticated media streaming and short-lived signed delivery URLs (`T004` next).
- Player lifecycle, background audio, position resume, and authorized offline downloads (`T005`).
- Narrative planner/writer/validator, provider adapters, generation queue, budgets/cost ledger, production TTS or fine-tuning (`T006`, `T007`, `T010`, `T015`).
- Creator/reviewer web CMS and content versioning/branching editor (`T008`, `T009`).
- Payments, store receipts/entitlements, royalty settlement, analytics and commercial operations (`T011`).

## BLOCKED
- iOS native compilation/Simulator validation: requires macOS + Xcode hardware environment.
- Public/commercial launch (`T011`–`T014`): expert Vietnam classification/privacy review, documented per-asset rights/voice approval, security/auth/media foundation, mobile QA and store/payment gates remain unmet.

## Git / next task
- Active branch: `main` (tracking `origin/main`), containing all verified `T000`–`T003` work.
- Next: **T004 — Authenticated media streaming and signed delivery** (`READY`).
