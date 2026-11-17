# START HERE — AudioVerse project constitution

## Why this project exists
Vietnam-first mobile entertainment experience where people listen to legally sourced audio fiction (narrated or AI synthesized) and selectively branch through original/derivative-authorized interactive stories. Core output to the user is a compelling story, not a chatbot.

## Primary products
**Audio Library:** fixed, curated, licensed episodic audio, background/offline listening when authorized, resume, search, recommendations and subscription. **Interactive Stories:** canonical story graph, player choice, LLM narration as optional draft, TTS output and consistent persistent state. Each content item has distinct permissions.

## Startup target
Vietnamese adult audience initially; test thriller/mystery with an *original* short series. No claim that this genre has highest market demand. Avoid collection/processing of minors' data until age/safety controls are reviewed.

## Priorities
P0 = proof of core story/audio UX + compliance foundations; P1 = commercial minimum viable product after gates; P2 = advanced AI, recommendation, creator platform; P3 = long-term R&D. P0 does not imply production-ready.

## Truth table (2026-11-17)
- **DONE for local demo:** FastAPI API, original 11-scene/3-ending graph, deterministic transitions, SQLite run/events + idempotency, basic rights checks; 17 tests passed in the 2026-11-17 takeover audit. All 11 MP3 HTTP responses and sample Range 206 verified. This is not production acceptance.
- **PARTIAL:** browser HTTP/assets verified, but actual browser/audio listening was not repeated in the takeover session. SQLite append-only history is an application convention, not DB-enforced immutability. See `agent/ONBOARDING_AUDIT_20261117.md`.
- **Source only / not executed in build container:** Flutter `mobile/lib` UI for listing, play, and choices. No generated Android/iOS wrappers; native toolchain unavailable here.
- **Not implemented:** remote LLM orchestration, vendor TTS, AI branching/free text, content licensing admin approvals, account authentication, licensed audio ingestion, proper offline/DRM, paid transactions, production Postgres, cloud architecture, analytics, moderation, commercial/legal review.

## Decision that affects all future work
User experience must tolerate **passive listening**. Branching is opt-in. The narrative engine must preserve authored invariants and meaningful decisions; AI does not change canonical facts. Production must not rely on an arbitrary "verified=true" JSON field.

## Reading order for humans
PRD -> FUNCTIONAL_SPEC -> UX_JOURNEYS -> ARCHITECTURE -> NARRATIVE_ENGINE -> AUDIO_TTS -> DATA_MODEL -> LEGAL_RIGHTS_RELEASE_GATES -> SECURITY -> TEST_STRATEGY -> PROJECT_STATE -> CURRENT_TASK.

## Owner's success definition
A small group of Vietnamese users completes the original interactive story, can hear the narrative smoothly, notices meaningful consequences, wants to hear another chapter, and—after lawful release—is willing to pay. Infrastructure, content cost and latency must be measurable per session.
