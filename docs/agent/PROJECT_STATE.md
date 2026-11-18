# PROJECT_STATE — Canonical project memory

**Updated:** 2026-11-18 | **Stage:** R1 in progress (`T000`, `T001`, `T002` DONE; `T003` Auth & Postgres next) | **Task completed:** T002 Content rights schema, contract and evidence review design

Evidence: [ONBOARDING_AUDIT_20261117.md](ONBOARDING_AUDIT_20261117.md), [T001_FLUTTER_BOOTSTRAP.md](../tasks/T001_FLUTTER_BOOTSTRAP.md), [T002_RIGHTS_PROVENANCE.md](../tasks/T002_RIGHTS_PROVENANCE.md), and [SESSION_LOG.md](SESSION_LOG.md).

## DONE — verified locally, not production acceptance
- FastAPI catalog/work/rights/run/choice/history API and loopback HTTP/static delivery.
- Original demo graph: 11 scenes, all authored branches reachable, exactly 3 reachable endings.
- Deterministic flag/precondition transitions; SQLite transactional run/event writes; choice idempotency, stale-version rejection, malformed-input rejection and demo actor scoping.
- **T002 Canonical Rights Provenance & Maker-Checker Policy Engine (`backend/audioverse/rights.py`, `backend/audioverse/content.py`, `content/licenses/demo_license.json`):**
  - Typed `RightsGrant`, `ContractEvidence`, `ChainOfTitle`, `ReviewAuditEntry`, `AssetLicense`, and `RightsManifest` models enforcing separate `stream`, `offline`, `derivative`, `tts`, `voice_clone`, and `training` permissions (`RGT-01`..`RGT-14`).
  - Deterministic fail-closed evaluation for action scope, chain-of-title completeness (`literary_author`, `translation_holder`, `adaptation_holder`, `performer_holder`, `master_recording_holder`, `voice_consent_holder`), territory, language, edition, validity window (`valid_from`/`expires_at`), 60/30/7-day renewal warnings, asset quarantine status, SHA-256 asset digest verification across all 11 demo MP3s, prohibited public scrape URLs (`youtube.com`, `tiktok.com`, `soundcloud.com`, `spotify.com`, `.rss`), dispute hold, and takedown freeze.
  - Maker-checker workflow transitions (`submit_evidence -> begin_review -> approve_grant`) blocking creator self-approval (`RIGHTS_SELF_APPROVAL_FORBIDDEN`).
- **T001 Flutter Bootstrap & Android Emulator E2E Validation:**
  - Flutter `3.50.0` (Dart `3.14.0`) at `D:\flutter` and Android SDK (`platforms;android-35/36`, `build-tools;35.0.0/36.0.0`, `ndk;28.2.13676358`, `cmake;3.22.1`, `emulator` `37.2.13.0`, `platform-tools` `37.0.1`) at `D:\Android\Sdk`.
  - Native `mobile/android` and `mobile/ios` wrappers, debug-only `network_security_config.xml`, `SceneAudioController` abstraction, committed-choice before audio-load recovery, pending `idempotency_key` retention, and `409` auto-refresh via `getRun`.
  - `flutter analyze` (**0 issues**), `flutter test` (**6/6 widget tests passed**), `flutter build apk --debug`, and live headless Android 15 (API 35) emulator E2E verification all passed.
- Windows Python 3.13.9 isolated `.venv`: **25 backend tests passed, 1 Starlette/httpx deprecation warning**. Repository check: **11 scenes, 182 requirements**. Compilation, full configured Ruff, JavaScript syntax, and pip dependency consistency pass.

## PARTIAL — code or limited checks, acceptance incomplete
- Browser experience: HTML/JS/CSS and HTTP path verified, plus live browser verification of `http://127.0.0.1:8765/` and Flutter Web preview `http://127.0.0.1:8766/`; Web `choose()` catch block in `web/app.js` still calls `render(current)` which can overwrite error text.
- Mobile iOS & background lifecycle: `mobile/ios` wrapper generated, but iOS build/Simulator execution requires macOS/Xcode (unrun on Windows). Persistent cross-restart run/position storage, background audio (`audio_service`), lockscreen controls, and offline downloads remain deferred to `T005`.
- Rights persistence & authenticated reviewer identity: `T002` implements the in-memory/manifest domain schema, maker-checker state transitions, and fail-closed evaluator; relational persistence of rights grants and authenticated staff RBAC are part of `T003` and `T008`.
- SQLite event history is append-only by application convention. No DB UPDATE/DELETE guard, tamper evidence, replay restore or immutable edition hash in DB is implemented yet (`T003`/`T009`).

## PLANNED — not implemented
- Real accounts/auth/RBAC; Postgres/SQLAlchemy/migrations; tenant isolation (`T003` next).
- Private media authorization and short-lived signed delivery URLs (`T004`).
- Fixed-audio edition/library management, search, background/offline playback, position sync, passive default route and process/network recovery (`T005`, `T009`).
- Creator/reviewer web CMS and ingestion pipeline (`T008`).
- Narrative planner/writer/validator, provider adapters, generation queue, budgets/cost ledger, production TTS or fine-tuning (`T006`, `T007`, `T010`, `T015`).
- Payments, store receipts/entitlements, royalty settlement, analytics and commercial operations (`T011`).

## BLOCKED
- iOS native compilation/Simulator validation: requires macOS + Xcode hardware environment.
- Public/commercial launch (`T011`–`T014`): expert Vietnam classification/privacy review, documented per-asset rights/voice approval, security/auth/media foundation, mobile QA and store/payment gates remain unmet.

## Git / next task
- Active branch: `main` (tracking `origin/main`), containing all verified `T000`, `T001`, and `T002` work.
- Next: **T003 — Postgres, migrations, user auth and tenant isolation design** (`READY`).
