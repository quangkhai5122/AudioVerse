# CURRENT_TASK — one next engineering packet

**Next:** T006 — Narrative AI provider adapters & schema verifier
**Implementation:** READY, not started
**Previous:** T005 — Player lifecycle, offline/resume/background plan DONE on `main`
**Authorization:** ordinary local development/commit/push on `main` is pre-authorized; deployment/store/content publication/paid inference is not.

## Exact next commands (PowerShell, repository root)

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=".venv\pytest_tmp"; Remove-Item -Recurse -Force ".venv\pytest_tmp" -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe scripts/check_repo.py
```

Read `AGENTS.md`, `docs/agent/PROJECT_STATE.md`, `docs/agent/BACKLOG.md`, latest `docs/agent/SESSION_LOG.md`, `docs/tasks/T006_NARRATIVE_ADAPTERS.md`, `docs/engineering/NARRATIVE_ENGINE.md`, and `docs/engineering/AI_EVALUATION.md` before editing.

## Objective & Scope for T006
- Implement swappable narrative provider gateway (`NAR-02`), canonical character/world bible validation (`NAR-03`), strict scene planner & writer JSON schema verification (`NAR-04`, `NAR-05`), deterministic world-state contradiction checks (`NAR-06`), episodic memory retrieval (`NAR-07`), prompt/usage logging & token/cost caps (`NAR-08`, `NAR-09`), prompt-injection boundary defense (`NAR-10`, `SEC-05`), safety moderation gate (`NAR-11`), and bounded retry with authored fallback (`NAR-12`) without making any paid external API calls in CI/demo.

## Acceptance criteria
- [ ] Provider gateway enforces `derivative` rights (`RGT-06`), explicit enable flag (`ai_enabled`), token/cost budget caps (`NAR-09`), bounded retries, and safe authored fallback (`NAR-12`).
- [ ] Strict JSON schema validator and deterministic world-state verifier reject hallucinated flags, dead scene targets, forbidden character trait mutations, and prompt-injection payloads (`NAR-03`–`NAR-06`, `NAR-10`, `SEC-05`).
- [ ] Relevant `NAR-*` and `SEC-05` requirement statuses updated in `docs/product/requirements.psv` and regenerated in `docs/product/FUNCTIONAL_SPEC.md`.
- [ ] Backend tests, repository check, Ruff, and Flutter `analyze`/`test` remain green; commit and push directly to `origin/main`.
