# Changelog

## T005 player lifecycle, progress resume, speed/sleep/seek controls & offline leases — 2026-11-18
- Added Migration `004_playback_progress_library_and_offline_leases` (`position_ms` & `playback_speed` on `runs`, `user_library` follow table, `offline_leases` table).
- Implemented playback progress write-back (`POST /api/v1/runs/{run_id}/progress`), continue-listening resume (`GET /api/v1/me/continue-listening`), library follow toggles (`POST /api/v1/me/library/{work_id}`, `GET /api/v1/me/library`), and license-scoped offline lease creation/validation (`POST /api/v1/downloads/leases`, `GET /api/v1/downloads/leases/{lease_id}/validate`) enforcing `offline` rights, entitlement status, storage quota (`OFFLINE_STORAGE_QUOTA_EXCEEDED`), and lease expiry (`OFFLINE_LEASE_EXPIRED`) (`CAT-07`, `CAT-08`, `LIB-01`, `LIB-02`, `PLY-05`–`PLY-08`, `PLY-11`, `PLY-13`, `PLY-14`, `PLY-18`, `INT-12`).
- Updated Flutter `StoryScreen` and `SceneAudioController` with `WidgetsBindingObserver` background pause write-back, automatic run/position/speed resume, `-10s`/`+10s` seek clamped to duration, `0.8x`–`2.0x` playback speed selector, sleep timer, audio focus interruption handling, and offline lease expiry validation; fixed `web/app.js` `A08` error preservation and `409` refresh.
- Expanded test suite to 35 passing backend tests and 7 passing Flutter widget tests.

## T004 authenticated media streaming & signed delivery — 2026-11-18
- Implemented private audio object registry (`media_objects`), `user_entitlements` (`stream` vs `offline`), redacted `media_delivery_logs`, short-lived HMAC-SHA256 signed media authorization (`POST /api/v1/playback/authorize`), and signed Range-capable delivery (`GET /api/v1/media/{asset_id}?token=...`) in `backend/audioverse/media.py` (`PLY-10`, `PLY-15`, `SEC-09`).
- Revalidated token TTL, signature, actor binding, active device session (honoring logout immediately), entitlement status, `cache_epoch` (`POST /api/v1/admin/media/{asset_id}/invalidate`), rights version, and live rights/quarantine/takedown status at delivery time.
- Expanded backend test suite to 33 passing tests.

## T003 user authentication, RBAC, migrations, edition pinning & replay recovery — 2026-11-18
- Implemented scrypt password hashing, HMAC-SHA256 Bearer tokens, revocable `device_sessions`, token refresh rotation, idempotent guest-to-account migration, personal data export, account deletion/anonymization, and RBAC with hash-chained `security_audit_log` in `backend/audioverse/auth.py` (`ACC-01`–`ACC-07`, `ACC-10`, `SEC-01`, `SEC-02`, `SEC-07`, `SEC-12`, `SEC-14`).
- Added versioned schema migrations (`schema_migrations`), DB-level `BEFORE UPDATE/DELETE` immutability triggers on `events` and `security_audit_log`, immutable `edition_id` pinning (`editions`, `INT-08`), `story_snapshots`, deterministic event replay recovery (`POST /api/v1/runs/{run_id}/restore`, `INT-18`), and PostgreSQL target DDL with Row-Level Security (`RLS`).
- Expanded backend test suite to 30 passing tests.

## T002 content rights provenance & maker-checker policy engine — 2026-11-18
- Implemented canonical `RightsGrant`, `ContractEvidence`, `ChainOfTitle`, `ReviewAuditEntry`, `AssetLicense`, and `RightsManifest` models and fail-closed policy evaluator in `backend/audioverse/rights.py` (`RGT-01`–`RGT-14`).
- Enforced maker-checker workflow (`submit_evidence -> begin_review -> approve_grant`) blocking creator self-approval, prohibited public scrape URLs (YouTube/TikTok/SoundCloud/Spotify/RSS), territory/language/edition/time windows, 60/30/7-day renewal warnings, asset quarantine, SHA-256 verification across all 11 demo MP3s, dispute holds, and takedown freezes.
- Added `GET /api/v1/works/{story_id}/rights` and enriched catalog metadata with `edition_id`, `attribution`, and `voice_label`; expanded backend test suite to 25 passing tests.

## T001 Flutter bootstrap & Android emulator validation — 2026-11-18
- Installed Flutter 3.50.0 (Dart 3.14.0) and Android SDK/NDK/CMake/Emulator on workstation; generated native `mobile/android` and `mobile/ios` project scaffolding and `pubspec.lock`.
- Configured debug-only loopback cleartext HTTP (`10.0.2.2`, `127.0.0.1`, `localhost`) via Android debug `network_security_config.xml` without weakening release manifests.
- Added `SceneAudioController` abstraction, `ApiException`, and `AudioVerseApi.getRun`; fixed `CatalogScreen` `setState` returning `Future` bug; updated `StoryScreen` to commit server run state before audio load, retain pending idempotency key on transport errors, and auto-refresh on HTTP 409.
- Verified `flutter analyze` (0 issues), 6 deterministic widget tests, `flutter build apk --debug`, and live headless Android 15 (API 35) emulator end-to-end flow (`s0 -> s1 -> s3 -> s4 -> s8`) against local FastAPI backend.

## T000 onboarding audit — 2026-11-17
- Verified Windows/Python backend, repository, lint and loopback HTTP/media baseline; retained unrun Flutter/browser/device checks explicitly.
- Persisted owner-authorized long-term commit/push and handoff protocol; audited roadmap and T001 toolchain prerequisites.
- Corrected eight existing one-line-statement lint issues and seven import-order issues; ignored generated egg-info. No product/API/story/rights change.

## 0.1.0 — 2026-11-17
- Original 11-scene mystery with three authored endings and local synthetic narration.
- FastAPI catalog/run/choice/scene streaming and browser UI.
- Deterministic canonical state engine, SQLite run/event storage and idempotent API.
- Flutter Android/iOS client source starter (native wrappers/toolchain verification pending).
- Long-term agent operating manual, 182 functional requirements, 16 task packets, eight ADRs.
- Legal/rights/voice/AI and commercial-release gates intentionally NOT passed.
