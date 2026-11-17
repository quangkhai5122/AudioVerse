# CURRENT_TASK — one next engineering packet

**Next:** T002 — Content rights schema, contract and evidence review design
**Implementation:** READY, not started
**Previous:** T001 — Flutter Bootstrap & Device Validation DONE (Android-first verified on API 35 emulator; iOS requires macOS/Xcode)
**Authorization:** ordinary local development/commit/push is pre-authorized; deployment/store/content publication is not.

## Exact next commands (PowerShell, repository root)

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=".venv\pytest_tmp"; Remove-Item -Recurse -Force ".venv\pytest_tmp" -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe scripts/check_repo.py
```

Read `AGENTS.md`, `docs/agent/PROJECT_STATE.md`, `docs/agent/BACKLOG.md`, latest `docs/agent/SESSION_LOG.md`, `docs/tasks/T002_RIGHTS_PROVENANCE.md`, and `docs/operations/LEGAL_RIGHTS_RELEASE_GATES.md` before editing.

## Objective & Scope for T002
- Design and implement the canonical `RightsGrant`, `ContractEvidence`, and `AssetLicense` schema and validator in the backend (`backend/audioverse/content.py` or a dedicated `rights.py` module while preserving backward compatibility for existing callers/tests).
- Enforce distinct action scopes (`stream`, `offline`, `derivative`, `tts`, `voice_clone`, `training`), effective term (`valid_from` / `expires_at`), territory, takedown/revocation status, and maker-checker review state (`DRAFT -> EVIDENCE_SUBMITTED -> UNDER_REVIEW -> APPROVED -> PUBLISHED -> EXPIRING -> EXPIRED/REVOKED/TAKEDOWN`) where a creator cannot self-approve real content.
- Keep `demo_license.json` working for local demo mode while ensuring production/non-demo checks fail closed on missing contract evidence, unauthenticated/missing reviewer, expired grants, territory mismatch, revoked/takedown status, derivative use on stream-only grants, or unauthorized voice cloning/training.

## Acceptance criteria
- [ ] Typed rights/provenance models and deterministic policy evaluation implemented with full backward compatibility for existing demo routes.
- [ ] Unit and API negative tests cover missing grant, expired term, territory mismatch, stream-only vs. derivative, unauthorized voice_clone/training, self-approval rejection, and takedown/revocation freeze.
- [ ] Relevant `RGT-*` requirement statuses updated in `docs/product/requirements.psv` and regenerated in `docs/product/FUNCTIONAL_SPEC.md`.
- [ ] Backend tests, repository check, Ruff, and Flutter `analyze`/`test` remain green; update task/state/backlog/log with exact execution evidence.
