# PROJECT_STATE — Canonical project memory

**Updated:** 2026-11-17 | **Stage:** R0 audited local prototype / R1 not accepted | **Task completed:** T000 onboarding audit

Evidence: [ONBOARDING_AUDIT_20261117.md](ONBOARDING_AUDIT_20261117.md). Earlier packaging claims in RELEASE_AUDIT are historical, not fresh device/browser evidence.

## DONE — verified locally, not production acceptance
- FastAPI catalog/work/run/choice/history API and loopback HTTP/static delivery.
- Original demo graph: 11 scenes, all authored branches reachable, exactly 3 reachable endings.
- Deterministic flag/precondition transitions; SQLite transactional run/event writes; choice idempotency, stale-version rejection, malformed-input rejection and demo actor scoping.
- Illustrative rights action checks deny absent/disabled grants, voice_clone and training. No authenticated legal review is implied.
- All 11 packaged MP3s return HTTP 200; sample byte range returns 206. File delivery is verified; listening quality is not.
- T000 documentation/code comparison, environment baseline, standing owner workflow and handoff recorded. Eight E701 formatting issues and seven import-order issues repaired without feature/API changes.
- Windows Python 3.13.9 isolated `.venv`: **17 tests passed, 1 Starlette/httpx deprecation warning**. Repository check: **11 scenes, 182 requirements**. Compilation, full configured Ruff, JavaScript syntax and pip dependency consistency pass.

## PARTIAL — code or limited checks, acceptance incomplete
- Browser experience: HTML/JS/CSS and HTTP path verified; no real browser/audio listening or automated browser E2E in this session. Choice error text can be overwritten by `render(current)` (static finding).
- Flutter catalog/story/foreground player source and one widget smoke exist. No Android/iOS wrappers or pubspec.lock; analyze/test/build/device playback not executed.
- Rights JSON checks permissions only; no expiry, territory, evidence validation, authenticated reviewer or revocation workflow.
- SQLite event history is append-only by application convention. No DB UPDATE/DELETE guard, tamper evidence, replay restore or immutable edition hash is implemented.
- CI workflow exists for Ubuntu/Python 3.11; local results use Windows/Python 3.13.9. Remote CI results must be recorded separately from local passes.

## PLANNED — not implemented
- Real accounts/auth/RBAC; Postgres/migrations; private media authorization; rate limiting, backups and production privacy/security controls.
- Fixed-audio edition/library management, search, background/offline playback, position sync, passive default route and process/network recovery.
- Canonical content/rights provenance schema, reviewer/CMS/creator ingestion and licensed human recordings.
- Narrative planner/writer/validator, provider adapters, generation queue, budgets/cost ledger, production TTS or fine-tuning. Existing AI classes are deterministic/disabled stubs and are not wired into live generation.
- Payments, store receipts/entitlements, royalty settlement, analytics and commercial operations.

## BLOCKED
- T001 execution: Flutter/Dart not in PATH; SDK not found in checked common locations, no adb/emulator available in PATH. Obtain/verify toolchain in the next T001 session. iOS native validation also needs macOS/Xcode.
- Public/commercial launch: expert Vietnam classification/privacy review, documented per-asset rights/voice approval, security/auth/media foundation, mobile QA and store/payment gates remain unmet. Legal documents were inventoried, not independently legally validated.

## Important verified limitations
- `X-Demo-Actor` is spoofable and defaults to a shared actor; scoping tests are not real authentication.
- Loopback is the launcher default, **not an enforced bind restriction**: AUDIOVERSE_HOST or a direct ASGI launcher can expose the demo. Never use a LAN/public bind.
- Story runs pin only story_id, not immutable edition/version; editing the graph can invalidate existing runs.
- Clients create new idempotency keys per attempt and lack persisted retry reconciliation. Flutter assigns the new run only after audio loading; a committed choice plus audio failure can leave stale client state. These are static findings, not device reproductions.
- No real user data, paid AI, third-party audio, deployment or T001 implementation was introduced.

## Git / next task
- Initial baseline: unborn main, no history/tracked files; 117 starter files including checksum manifest. Origin verified as the empty public `quangkhai5122/AudioVerse` repository with owner push access.
- Working branch: `codex/t000-onboarding-audit`; standing routine commit/push permission recorded in AGENTS and OWNER_DECISIONS. See SESSION_LOG for the observed commit/push outcome; never infer it from this plan.
- Next: **T001 — Flutter Bootstrap & Device Validation** (not implemented). Resolve SDK availability, then analyze/widget tests, Android debug build and emulator catalog/audio/choice/error validation. Keep T002 rights provenance and T003 security dependencies in backlog.
