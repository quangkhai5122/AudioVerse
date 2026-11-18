# CURRENT_TASK — one next engineering packet

**Next:** T003 — Postgres, migrations, user auth and tenant isolation design
**Implementation:** READY, not started
**Previous:** T002 — Content rights schema, contract and evidence review design DONE on `main`
**Authorization:** ordinary local development/commit/push on `main` is pre-authorized; deployment/store/content publication is not.

## Exact next commands (PowerShell, repository root)

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=".venv\pytest_tmp"; Remove-Item -Recurse -Force ".venv\pytest_tmp" -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe scripts/check_repo.py
```

Read `AGENTS.md`, `docs/agent/PROJECT_STATE.md`, `docs/agent/BACKLOG.md`, latest `docs/agent/SESSION_LOG.md`, `docs/tasks/T003_AUTH_POSTGRES.md`, `docs/engineering/DATA_MODEL.md`, and `docs/operations/SECURITY_PRIVACY.md` before editing.

## Objective & Scope for T003
- Replace spoofable `X-Demo-Actor` in non-demo / authenticated routes with signed session/token authentication and role-based access control (`listener`, `creator`, `legal_reviewer`, `rights_officer`, `compliance_admin`) while preserving local demo compatibility where explicitly configured.
- Introduce relational schema/migrations and append-only/tamper-evident event protections, pinning `story_runs` to `edition_id` and scoping user runs strictly to authenticated user identities so User A can never access User B's run or history.

## Acceptance criteria
- [ ] User A cannot read or mutate User B's story run or events; unauthenticated/expired/revoked tokens are denied (`401`/`403`).
- [ ] Role escalation attempts (e.g. listener/creator attempting reviewer actions) are denied and auditable (`ACC-10`, `SEC-01`, `SEC-02`).
- [ ] Database schema migration and deterministic event replay/snapshot recovery tests pass while preserving local demo tests.
- [ ] Relevant `ACC-*` and `SEC-*` requirement statuses updated in `docs/product/requirements.psv` and regenerated in `docs/product/FUNCTIONAL_SPEC.md`.
- [ ] Backend tests, repository check, Ruff, and Flutter `analyze`/`test` remain green; commit and push directly to `origin/main`.
