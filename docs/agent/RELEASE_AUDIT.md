# Starter artifact acceptance audit — 2026-11-17

**Historical packaging record.** These results describe the starter assembly environment. Current workstation evidence and corrected claim boundaries are in [ONBOARDING_AUDIT_20261117.md](ONBOARDING_AUDIT_20261117.md); do not treat this file as a fresh native/browser/security acceptance.

## Delivered functionality and evidence
- Backend FastAPI demo: health/case catalog/run create/run retrieve/choice/history/MP3/browser.
- Original 11-scene Vietnamese branching story, 3 endings, human-authored canonical logic.
- 11 synthetic eSpeak locally generated narration MP3s (technical fixture, no commercial voice QA).
- Deterministic state engine with author-defined preconditions/effects, SQLite transactional commits, event order and idempotent API.
- Rights gate manifest limited to locally original demo content; no real contracts or upload facilities.
- Flutter mobile `lib` source and a simple widget smoke (unexecuted due no Flutter SDK); platform native projects need generation.
- Agent docs, 182 function requirements, 16 task packets, 8 architecture decision records, finance/cost model and official link register.

## Verification performed
- `PYTHONPATH=backend python -m pytest -q`: **17 passed**.
- `python scripts/check_repo.py`: PASS for 11 scene graphs, assets, 182 requirements and handoff docs.
- `python -m compileall -q backend scripts`: PASS.
- `node --check web/app.js`: PASS.
- `python -m pip install --no-build-isolation --no-deps -e .`: completed with local installed dependencies.
- HTTP smoke via launched server: `/healthz` 200, `/` 200, `/docs` 200, `/api/v1/catalog` 200, `/api/v1/audio/s0.mp3` 200, POST `/api/v1/runs` 201.
- Zip integrity: package script executes `ZipFile.testzip()` for both artifacts.

## Not verified / not built
- Flutter SDK/native builds, Android/iOS compatibility, app signing, IAP, real user auth, rights-review workflow, LLM/TTS API, voice fine-tuning, streaming scale/CDN, real content licenses and Vietnamese legal classification. Nothing is production-cleared.

## Release gate state
Local demo artifact: acceptable for development and agent onboarding. Public/commercial app: **BLOCKED** pending the legal/security/content/billing gates in `LEGAL_RIGHTS_RELEASE_GATES.md`.
