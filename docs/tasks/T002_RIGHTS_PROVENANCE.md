# T002 — Rights Provenance

**Stage:** R1  |  **Status:** DONE  |  **Dependencies:** None; legal advisor review still required for commercial production  |  **As of:** 2026-11-18

## Objective and scope
Design and implement the canonical `RightsGrant`, `ContractEvidence`, `ChainOfTitle`, `ReviewAuditEntry`, `AssetLicense`, and `RightsManifest` schema in `backend/audioverse/rights.py` with separate `stream`, `offline`, `derivative`, `tts`, `voice_clone`, and `training` permissions, territory/language/edition/time-window enforcement, 60/30/7-day renewal alerts, takedown/dispute holds, prohibited public scrape URL rejection, and maker-checker review workflow (`submit_evidence -> begin_review -> approve_grant`) where a creator cannot self-approve real content.

## Acceptance & Evidence Checklist
- [x] Code checked into `backend/audioverse/rights.py`, `backend/audioverse/content.py`, `backend/audioverse/main.py`, `content/licenses/demo_license.json`, `scripts/check_repo.py`, and `backend/tests/test_rights.py`.
- [x] Relevant requirement IDs (`RGT-02` through `RGT-14`) in `docs/product/requirements.psv` and `docs/product/FUNCTIONAL_SPEC.md` updated from `PLANNED` to `DEMO`.
- [x] Exact tests run and results copied into `docs/agent/SESSION_LOG.md`:
  - `.\.venv\Scripts\python.exe -m pytest -v -p no:cacheprovider --basetemp=".venv\pytest_tmp"` => **25 passed, 1 warning**.
  - `.\.venv\Scripts\python.exe scripts/check_repo.py` => `Integrity PASS: 11 scenes, 182 requirements, assets and agent docs`.
  - `.\.venv\Scripts\python.exe -m ruff check backend scripts` => `All checks passed!`.
- [x] Negative cases, edge conditions and security/rights checks covered:
  - Stream-only grant denied on `offline`, `derivative`, `tts`, `voice_clone`, and `training`.
  - Creator self-approval rejected in both `begin_review`/`approve_grant` and `evaluate_rights` (`RIGHTS_SELF_APPROVAL_FORBIDDEN`).
  - Missing `translation_holder`, `adaptation_holder`, `performer_holder`/`master_recording_holder`, or `voice_consent_holder` fails closed.
  - Public scrape URLs (`youtube.com`, `youtu.be`, `tiktok.com`, `soundcloud.com`, `spotify.com`, `.rss`) rejected (`RIGHTS_UNAUTHORIZED_SOURCE_URL`).
  - Not-yet-valid, expired, wrong territory, wrong language, wrong edition, quarantined asset (`status="quarantine"`), corrupted asset SHA-256, dispute hold, and takedown freeze all fail closed with specific machine codes.
- [x] `PROJECT_STATE.md`, `CURRENT_TASK.md`, `BACKLOG.md`, and `SESSION_LOG.md` updated.
- [x] Clear next task (`T003 — Auth & Postgres`) and reproducible first command recorded.

## Known risks and out-of-scope
Public production access remains blocked until qualified legal counsel reviews actual content contracts and Vietnam online-game/service classification (`T012`), and until real user authentication and RBAC (`T003`) replace `X-Demo-Actor`.
