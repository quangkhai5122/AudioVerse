# Verification strategy and release quality

## Layered test pyramid
- **Unit:** pure state-machine preconditions/effects, story graph validation, rights decision matrix, unit rounding of AI cost, price arithmetic, content age and version gates.
- **API integration:** FastAPI routes with temporary DB; idempotency replay, stale versions, Bearer token auth, device session rotation/revocation, RBAC & audit chain, guest migration, edition pinning, deterministic replay recovery, rights provenance/quarantine/takedown gates, signed media URL authorization & byte-range delivery, and synthetic MP3 output. Current suite totals 33 backend tests (7 API, 6 engine/rights/AI, 1 full graph, 3 cost-model, 8 rights provenance & maker-checker, 5 auth/RBAC/migrations/replay, 3 secure media & signed delivery) plus 6 Flutter widget tests. Windows/Python 3.13.9: 33 passed, one Starlette/httpx warning.
- **Contract:** OpenAPI client compatibility, schema migrations, app-store webhook signatures, provider request/response fixtures (no paid calls in CI).
- **Mobile widget/device:** Flutter catalog/player/choice flows, Android+iOS audio focus, lockscreen controls, background, re-open, offline, weak network, 3G, phone calls, screen readers; **not run in packaging environment**.
- **Production E2E:** verified entitlement, secure stream, creator ingestion with rights reviewer, takedown, payment refund/restore, AI generation retries and no-double-bill.
- **Security and chaos:** permission matrix denial, prompt injection, rate limit, provider timeout, queue crash, DB failover, backup restore, loss of CDN authorization and rights expiry.
- **Human editorial:** consistency, style, voice listening quality and age ratings; no replacement by AI-only judge.

## MVP test acceptance
- No demo invalid action accepted; stale edit rejected and event log unchanged.
- All authored demo branches reachable and every ending valid; no dead node.
- Retries with same idempotency key produce one event and exact response.
- Browser can play all sample audio and navigate story (manual smoke).
- Mobile Android emulator and iOS simulator passes core UI+player, after T001.
- Rights failed states block streams/derivatives; production reviewer gate not yet implemented.

## Launch block conditions
Any known cross-account read, unlicensed media distribution, payment double-charge, invalid story state transition, content age compliance breach, inability to restore backups, or uncontrolled provider spending blocks public release. Legal classifications/permits are external release gates.

## Recommended CI
GitHub Actions Python setup, `pip install -e .[dev]`, `pytest`, `python scripts/check_repo.py`, `python -m compileall`; optional Ruff lint after baseline. Add Flutter setup/analyze/widget tests as a separate job once native toolchain and platform directories are generated. Keep paid AI contract tests in controlled environments with explicit budget approval.

## Bug template
Expected vs actual; OS/app version; work/edition/run/scene id (redacted), AI provider and prompt digest, timestamp/request_id, reproduction, test failure, rights implications, urgency, rollback decision. Never put raw user voice or copyrighted story into public bug tickets.
