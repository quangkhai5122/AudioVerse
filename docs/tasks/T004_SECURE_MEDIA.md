# T004 — Secure Media Streaming & Signed Delivery

**Stage:** R1  |  **Status:** DONE  |  **Dependencies:** T002 (done), T003 (done)  |  **As of:** 2026-11-18

## Objective and scope
Implement the private audio object registry (`media_objects`), entitlement checks (`user_entitlements` distinguishing `stream` vs `offline`), playback authorization endpoint (`POST /api/v1/playback/authorize`), short-lived HMAC-SHA256 signed media delivery endpoint (`GET /api/v1/media/{asset_id}?token=...`) with HTTP Range (`206 Partial Content`) support, cache invalidation (`POST /api/v1/admin/media/{asset_id}/invalidate`), and redacted delivery logs (`media_delivery_logs`), while keeping `/api/v1/audio/{scene_id}.mp3` available only when `allow_public_sample_audio=True`.

## Acceptance & Evidence Checklist
- [x] Code checked into `backend/audioverse/media.py`, `backend/audioverse/migrations.py`, `backend/audioverse/settings.py`, `backend/audioverse/main.py`, and `backend/tests/test_secure_media.py`.
- [x] Relevant requirement IDs (`PLY-10`, `PLY-15`, `SEC-09`) in `docs/product/requirements.psv` and `docs/product/FUNCTIONAL_SPEC.md` updated from `PLANNED` to `DEMO`.
- [x] Exact tests run and results copied into `docs/agent/SESSION_LOG.md`:
  - `.\.venv\Scripts\python.exe -m pytest -v -p no:cacheprovider --basetemp=".venv\pytest_tmp"` => **33 passed, 1 warning**.
  - `.\.venv\Scripts\python.exe scripts/check_repo.py` => `Integrity PASS: 11 scenes, 182 requirements, assets and agent docs`.
  - `.\.venv\Scripts\python.exe -m ruff check backend scripts` => `All checks passed!`.
- [x] Negative cases, edge conditions and security/rights checks covered:
  - Tampered signature (`401 MEDIA_TOKEN_INVALID_SIGNATURE`), expired token (`401 MEDIA_TOKEN_EXPIRED`), cross-asset substitution (`403 MEDIA_ASSET_MISMATCH`), cross-user URL access (`403 MEDIA_ACTOR_MISMATCH`), and logged-out device session (`401 AUTH_SESSION_REVOKED`) all fail closed with `Cache-Control: no-store`.
  - Stream-only entitlement is denied on `action="offline"` (`403 OFFLINE_ENTITLEMENT_REQUIRED`); revoking an entitlement immediately blocks already-minted signed URLs at delivery (`403 ENTITLEMENT_EXPIRED`).
  - Staff cache invalidation (`POST /api/v1/admin/media/{asset_id}/invalidate`) increments `cache_epoch` and blocks stale signed URLs (`403 MEDIA_CACHE_INVALIDATED`).
  - Full `200 OK` and byte-range `206 Partial Content` (`Range: bytes=0-31`) verified along with `416 RANGE_NOT_SATISFIABLE` on out-of-bounds ranges.
- [x] `PROJECT_STATE.md`, `CURRENT_TASK.md`, `BACKLOG.md`, and `SESSION_LOG.md` updated.
- [x] Clear next task (`T005 — Player Lifecycle`) and reproducible first command recorded.

## Known risks and out-of-scope
Cloud CDN/R2 edge worker deployment and HLS multi-bitrate packaging belong to staging/cloud operations (`T012`/`T014`). Mobile player lifecycle, background audio, position resume, and offline download storage are next in `T005`.
