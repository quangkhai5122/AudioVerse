# T003 — Auth Postgres & Migrations

**Stage:** R1  |  **Status:** DONE  |  **Dependencies:** T002 schema (done); T001 client contract (done)  |  **As of:** 2026-11-18

## Objective and scope
Replace spoofable demo actor header in authenticated mode (`allow_demo_header=False` and `/api/v1/auth/*`, `/api/v1/me*`, `/api/v1/admin/*`) with signed Bearer token authentication, revocable `device_sessions`, role-based access control (`listener`, `creator`, `legal_reviewer`, `rights_officer`, `compliance_admin`), guest-to-account migration, personal data export/deletion, versioned schema migrations (`schema_migrations`), DB-level append-only immutability triggers (`events`, `security_audit_log`), immutable `edition_id` pinning (`editions`), deterministic event replay recovery (`story_snapshots` + `restore_run_from_events`), and PostgreSQL target DDL with Row-Level Security (`RLS`), while preserving local demo compatibility when `allow_demo_header=True`.

## Acceptance & Evidence Checklist
- [x] Code checked into `backend/audioverse/auth.py`, `backend/audioverse/migrations.py`, `backend/audioverse/storage.py`, `backend/audioverse/settings.py`, `backend/audioverse/main.py`, and `backend/tests/test_auth_postgres.py`.
- [x] Relevant requirement IDs (`ACC-01`..`ACC-07`, `ACC-10`, `INT-08`, `INT-18`, `SEC-01`, `SEC-02`, `SEC-07`, `SEC-12`, `SEC-14`) in `docs/product/requirements.psv` and `docs/product/FUNCTIONAL_SPEC.md` updated from `PLANNED` to `DEMO`.
- [x] Exact tests run and results copied into `docs/agent/SESSION_LOG.md`:
  - `.\.venv\Scripts\python.exe -m pytest -v -p no:cacheprovider --basetemp=".venv\pytest_tmp"` => **30 passed, 1 warning**.
  - `.\.venv\Scripts\python.exe scripts/check_repo.py` => `Integrity PASS: 11 scenes, 182 requirements, assets and agent docs`.
  - `.\.venv\Scripts\python.exe -m ruff check backend scripts` => `All checks passed!`.
- [x] Negative cases, edge conditions and security/rights checks covered:
  - User A cannot read, mutate, list events, or restore User B's run (`404` tenant isolation).
  - Unauthenticated requests to private routes when `allow_demo_header=False` are rejected (`401 AUTH_REQUIRED`), even if `X-Demo-Actor` is provided.
  - Expired tokens (`401 AUTH_TOKEN_EXPIRED`), rotated access tokens (`401 AUTH_TOKEN_ROTATED`), replayed refresh tokens (`401 AUTH_INVALID_REFRESH_TOKEN` + automatic session revocation), and revoked sessions (`401 AUTH_SESSION_REVOKED`) all fail closed.
  - Privilege escalation attempts (`listener` calling `/api/v1/admin/security-audit`) are denied (`403 RBAC_ROLE_DENIED`) and recorded in the hash-chained `security_audit_log`.
  - Direct SQL `UPDATE` or `DELETE` on `events` or `security_audit_log` is blocked by database triggers (`append-only and immutable`).
  - Existing runs resolve against their pinned `edition_id` (`editions`) even after the live story graph is modified (`INT-08`), and deterministic replay recovery (`POST /api/v1/runs/{run_id}/restore`, `INT-18`) verifies the full `event_hash` chain.
- [x] `PROJECT_STATE.md`, `CURRENT_TASK.md`, `BACKLOG.md`, and `SESSION_LOG.md` updated.
- [x] Clear next task (`T004 — Secure Media`) and reproducible first command recorded.

## Known risks and out-of-scope
Live cloud PostgreSQL provisioning, TLS termination, and external OAuth/passkey providers belong to staging/production infrastructure (`T012`/`T014`). Authenticated media streaming with short-lived signed URLs is next in `T004`.
