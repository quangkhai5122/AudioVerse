# CURRENT_TASK — one next engineering packet

**Next:** T004 — Authenticated media streaming and signed delivery
**Implementation:** READY, not started
**Previous:** T003 — Postgres, migrations, user auth and tenant isolation design DONE on `main`
**Authorization:** ordinary local development/commit/push on `main` is pre-authorized; deployment/store/content publication is not.

## Exact next commands (PowerShell, repository root)

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=".venv\pytest_tmp"; Remove-Item -Recurse -Force ".venv\pytest_tmp" -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe scripts/check_repo.py
```

Read `AGENTS.md`, `docs/agent/PROJECT_STATE.md`, `docs/agent/BACKLOG.md`, latest `docs/agent/SESSION_LOG.md`, `docs/tasks/T004_SECURE_MEDIA.md`, `docs/engineering/MEDIA_DELIVERY.md`, and `docs/operations/SECURITY_PRIVACY.md` before editing.

## Objective & Scope for T004
- Implement private audio object registry, playback authorization endpoint (`POST /api/v1/playback/authorize`), and short-lived HMAC-signed media URLs (`PLY-15`, `SEC-09`) with per-request rights revalidation (`stream` vs `offline`), token TTL expiration, actor/asset scoping, and byte-range playback support.
- Keep `/api/v1/audio/{scene_id}.mp3` working in local demo mode while ensuring signed media delivery denies unauthorized, expired, tampered, cross-user, or revoked/takedown requests.

## Acceptance criteria
- [ ] Playback authorization issues short-lived signed URLs/tokens scoped to user/actor, `work_id`, `edition_id`, `scene_id`/`asset_id`, action (`stream` or `offline`), and expiry timestamp.
- [ ] Unauthorized, expired, tampered, cross-asset, stream-only offline attempt, or post-takedown signed URL requests fail closed (`401`/`403`).
- [ ] HTTP Range (`206 Partial Content`) and cache-control headers (`private, no-store` or scoped max-age) are verified on signed media delivery.
- [ ] Relevant `PLY-15` and `SEC-09` requirement statuses updated in `docs/product/requirements.psv` and regenerated in `docs/product/FUNCTIONAL_SPEC.md`.
- [ ] Backend tests, repository check, Ruff, and Flutter `analyze`/`test` remain green; commit and push directly to `origin/main`.
