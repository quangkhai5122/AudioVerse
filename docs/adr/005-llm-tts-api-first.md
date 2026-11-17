# ADR-005: Model/provider abstraction, API baseline before training
**Status:** Accepted for starter **Date:** 2026-11-17

## Decision
API-driven LLM/TTS adapters behind rights, quotas, model/cost ledger and deterministic validator; keep remote inference disabled in the demo. Benchmark quality, latency and cost on Vietnamese original text before investing in model training.

## Rationale
A TTS model trained from unauthorized podcasts may violate voice/recording rights. Existing models/weights have diverse licenses. API cost is low for pre-rendered content but personalized generation scales per user.

## Revisit when
Commercial rights for datasets/voice/models are verified and API baseline shows a quantifiable reason for self-host/fine-tuning. No training solely because it is technologically interesting.
