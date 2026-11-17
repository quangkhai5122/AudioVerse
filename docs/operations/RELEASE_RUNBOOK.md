# Operational runbook: local, staging and future production

## Demo start on Windows
`py -3.11 -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install -e ".[dev]"; python -m audioverse.main`

## Demo start on Unix
`python3 -m venv .venv && source .venv/bin/activate && python -m pip install -e '.[dev]' && python -m audioverse.main`

Open localhost only. Data in `local_data/audioverse.db` (ignored). Delete this local file only after confirming no valuable development test sessions; use backup first if needed. Unit tests write in temp directories.

## Native Flutter local development
See `mobile/README.md`; platform bootstrap requires a locally installed Flutter/Xcode/Android toolchain, local backend bridge and debug-only network exceptions. Browser demo remains primary currently validated demo.

## Staging deployment (not done)
Do NOT point demo build to staging. First finish T003 auth, T004 authorized media, secrets, Postgres, privacy & rate limits, approval gate. Use separate identities, credentials, bucket, AI provider budgets. Ship only original internally approved media; no user private data from prod.

## Production release checklist (not done)
Compliance signoff + publish entity + store policies; rights reviewed and documented; production auth; secure media; backup/restore; incident exercises; app signing; IAP server validation; content moderation and takedown; SLO and alerts; rollout/rollback; approved user support policies. If any fail, do not launch.

## Incident severity
P0: wrong user sees a private story/voice/payment, unauthorized copyrighted audio distributed, confirmed billing replay, data loss. Freeze relevant service/rights immediately, preserve evidence and contact security/legal lead. P1: widespread playback broken, narrative corruption or global AI budget runaway. Kill switch provider/service and roll back. P2: limited isolated app crashes, TTS pronunciation error. Queue fixes with customer explanation.

## Metrics to watch
HTTP error rates; player startup failures; buffer stalls; app crashes; AI time-to-first-audio p95; invalid story transitions; paid request retry/charge count; token and TTS spend/day; content takedown latency; database storage/recovery, copyright reports, complaints.

## Do not automate on demo
No open CORS to all origins, no `0.0.0.0` bind, no live payment webhooks, no copying API keys into app, no public URLs to local MP3s, no rights auto-approval. These are engineering footguns that must be removed via dedicated tasks, not config toggles alone.
