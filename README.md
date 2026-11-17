# AudioVerse — Vietnamese Interactive Audio Fiction

**A working local reference repository + long-running AI Coding Agent handoff.**

> **Status (2026-11-17): developer proof of concept only.** The demo contains an original Vietnamese mystery, 11 short machine-generated MP3 excerpts, a deterministic branching engine, SQLite event log, idempotent transition API, basic rights gating, a browser demo, and a Flutter UI source starter. **No real AI model calls, commercial audio rights verification, user authentication, payments, production data protection, offline license enforcement, native Flutter build validation, game licensing, or commercial launch approval are implemented.**

## Quick start — Windows PowerShell

```powershell
cd audioverse-starter
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
$env:AUDIOVERSE_DB_PATH = "$PWD\local_data\audioverse.db"
python -m audioverse.main
```

Open `http://127.0.0.1:8765/` (web demo) and `http://127.0.0.1:8765/docs` (interactive API). The launcher defaults to localhost; the bind address is not enforced, so never override it with a LAN/public bind. The `media/demo/*.mp3` files are included. To regenerate synthetic recordings: `python scripts/generate_demo_audio.py` (requires espeak + ffmpeg).

## Quick start — macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m audioverse.main
```

## Run tests

```bash
python -m pytest
python -m compileall -q backend
```

Takeover audit on 2026-11-17: **17 backend tests passed** on Windows/Python 3.13.9, with one Starlette/httpx deprecation warning. Repository integrity, compilation, full configured Ruff, JavaScript syntax and loopback HTTP/11-MP3 delivery checks passed. Real browser listening and Flutter analyze/test/native/device validation were not run. See the [current audit](docs/agent/ONBOARDING_AUDIT_20261117.md) for exact evidence; earlier packaging claims are historical.

On the audited workstation, the Windows Store `python` alias and registered `py -3.14` are unusable. A local ignored environment was created with `& 'D:\miniconda3\python.exe' -m venv .venv`; use `.\.venv\Scripts\python.exe -m pytest` and `.\.venv\Scripts\python.exe scripts/check_repo.py`. Other machines should choose an installed Python >=3.11 rather than copying this machine-specific path.

## Project navigation

| Goal | Read first |
|---|---|
| Owner / Coding Agent entry point | [`AGENTS.md`](AGENTS.md), [`docs/agent/PROJECT_STATE.md`](docs/agent/PROJECT_STATE.md) |
| Product & complete roadmap | [`docs/product/PRD.md`](docs/product/PRD.md), [`docs/product/FUNCTIONAL_SPEC.md`](docs/product/FUNCTIONAL_SPEC.md) |
| Build architecture & API | [`docs/engineering/ARCHITECTURE.md`](docs/engineering/ARCHITECTURE.md), [`docs/engineering/API.md`](docs/engineering/API.md) |
| Narrative AI and TTS | [`docs/engineering/NARRATIVE_ENGINE.md`](docs/engineering/NARRATIVE_ENGINE.md), [`docs/engineering/AUDIO_TTS.md`](docs/engineering/AUDIO_TTS.md) |
| Copyright, content and game compliance | [`docs/operations/LEGAL_RIGHTS_RELEASE_GATES.md`](docs/operations/LEGAL_RIGHTS_RELEASE_GATES.md) |
| Cloud cost model | [`docs/finance/COST_MODEL.md`](docs/finance/COST_MODEL.md) |
| Agent task queue | [`docs/agent/BACKLOG.md`](docs/agent/BACKLOG.md), [`docs/tasks/`](docs/tasks/) |
| Progress between sessions / accounts | [`docs/agent/SESSION_LOG.md`](docs/agent/SESSION_LOG.md), [`docs/agent/HANDOFF_PROTOCOL.md`](docs/agent/HANDOFF_PROTOCOL.md) |

## What's in the repository

```text
backend/audioverse/     Python FastAPI demo, pure branching engine, SQLite event ledger
backend/tests/          Tests for story graph, authorization gate, idempotency, API
content/demo_story/     Original Vietnamese sample story (11 scenes)
content/licenses/       Demo-only content rights manifest
media/demo/             11 original synthetic narration clips; no Internet audio
web/                    Working localhost interactive browser experience
mobile/lib/             Flutter mobile source (Android/iOS templates not generated)
docs/product/           PRD, journeys, requirements, product research
docs/engineering/       API, architecture, story engine, AI, TTS, data, security
docs/operations/        Legal gates, content onboarding, testing, releases, incident response
docs/finance/           Assumption-based economics, hosting costs, pricing
scripts/                Demo audio producer, checks, project hygiene
docs/tasks/             Executable agent task packets with acceptance criteria
```

## Critical product decisions

1. **Two listening modes:** fixed/audio library and interactive original stories; do not treat every imported audio as derivative-licensed.
2. **Canonical state is deterministic:** the LLM may draft narration but may not invent canonical item possession, character death or episode progression.
3. **No unauthorized scraping, download or voice cloning.** Rights need provenance and review.
4. **Use API baseline before TTS/LLM fine-tuning.** Research only after QA + cost/latency benchmarks.
5. **No cloud production or payment launch until legal and security release gates pass.** Game classification for Vietnam is unresolved.
6. **Repository files are source of truth across agent sessions.** Update the tracked handoff documents at every completed task.

## Useful commands

```bash
python -m pytest
python scripts/check_repo.py
python scripts/generate_demo_audio.py  # optional, regenerates clips
```

Start a Coding Agent with [`scripts/agent_bootstrap_prompt.txt`](scripts/agent_bootstrap_prompt.txt). Do not tell it to begin with billing, AI self-training, Internet audio scraping, or production deployment.

## Licensing notes

`LICENSE` applies to starter source code. The demo story and locally synthesized audio are original sample materials created for this project; see `content/licenses/demo_license.json` and `CONTENT_LICENSE.md` for their separate status. Third-party software packages, model weights and acquired audio each have separate licenses. No claim of verified commercial licensing is made for future content.
