# AI evaluations, experimental design and model governance

## Model baseline hierarchy
Start with authored path + deterministic template; then stronger API LLM with schema and event-based fact checks; then compare lower-cost API; only then self-host/fine-tune if measured improvement. LLM selection must never be driven by model hype alone.

## Experiment register
E001: authored static vs LLM cosmetic variation; E002: free-text vs explicit choice; E003: narrative memory summary vs structured-state retrieval; E004: pre-render vs prefetch vs on-demand audio; E005: human opening narrator vs AI opening narrator (with valid grants); E006: provider TTS A/B over 30-minute listening; E007: small-model SFT vs zero/few-shot; E008: scene-length impact on p95 latency and conversion.

## Quality evaluation rubric (blind reviewer)
Narrative coherence (1–5), natural Vietnamese (1–5), suspense/pacing (1–5), character continuity (1–5), meaningful consequence (1–5), audio prosody (1–5), fatigue after 20 minutes (1–5). Reviewers compare blinded outputs and record reasons, not only an aggregate average. Two or more independent judges per test sample and adjudication for substantial disagreements.

## Hard automatic assertions
No characters resurrected without defined event; no impossible item use; no disclosure of future mystery solution; no deviation from edition/world rights; no hidden choice effect; no invented voice/creator credit; no harmful content outside rating. Assert plan schema and typed delta before calling TTS. Prompt injection and adversarial input must not access files, secrets, database or tool commands.

## Latency metrics
`choice_submit_to_commit_ms`, `commit_to_job_start_ms`, `llm_first_text_ms`, `tts_first_audio_ms`, `choice_to_audible_ms`, cache hit ratio, first byte from CDN, buffer underrun count. P50, p95, p99 by country/network/model/scene length. Separate pre-rendered and dynamic path populations.

## Cost metrics
Tokens in/out; batch vs online; characters billed by TTS; GPU seconds; storage write/read requests; cache misses; per-user request count; paid conversion by experiment. Include retry failures and moderation rejections in contribution margin.

## Experimental integrity
Pre-register a hypothesis and owner, deterministic randomization by anonymous stable user ID with consent; avoid exposing different safety rights by experiment; define exclusion/guardrail metrics; no overfitting on the same story. Retain model version/prompt digest and provenance of each generated sample.

## Eval dataset structure (planned)
`tests/fixtures/evals/{story_edition,seed_state,action,expected_preconditions,expected_delta,forbidden_facts,reference_lore,replay_trace}`; `human_reviews.csv` has anonymized reviewer ID, story version, score and explanation. Do NOT train on evaluation corpus or use copyrighted scripts without rights.

## Sign-off requirements
Any model/prompt change that reduces deterministic pass rate blocks release regardless of human prose preference. External model terms, data retention, content policy and privacy must be reviewed before sending stories or user choices to remote providers.
