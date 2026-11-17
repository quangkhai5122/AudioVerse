# Narrative engine — detailed technical specification

## Fundamental separation
Canonical event/state logic is **deterministic**. LLM drafts prose and suggestions; cannot directly modify canonical facts, user balances, rights or prior event history. This project uses a hybrid **authored directed graph + controlled generated variants** rather than fully unbounded text adventure.

## Formal model
A published story edition is a graph `G=(V,E)` with nodes scenes and directed choice edges. A run at time t has canonical state:

`S_t = (edition_id, scene_id, world_facts, inventory, relationships, quest_flags, time_index, event_cursor)`

Action `a_t` must belong to `AllowedActions(S_t)`. Transition `T(S_t,a_t)` is a pure function. Validation requires preconditions, effect type constraints, narrative bounds and rights. If any fail, no canonical write occurs.

`S_(t+1) = T(S_t, a_t)` and `event_(t+1) = {action_id, from_scene, to_scene, delta, version, seed, edition_hash}`.

Pre-rendered authored scene audio is preferred. For dynamic scene `D`, planner creates *proposed scene constraints*; writer creates textual prose; deterministic postvalidator checks references and permissible world effects, safety moderation checks content; TTS generates audio and the output is staged until approved. Run should commit the user choice once, and keep a separate render state that can fail/recover.

## State schema v1 proposal
```json
{
  "canon_version": 1,
  "scene_id": "s3",
  "inventory": {"key_b": true},
  "facts": {"vy_present": false, "archive_open": false},
  "relationship": {"vy_trust": 0},
  "time_index": 8,
  "quest_flags": ["tracks_seen"],
  "event_cursor": 3
}
```

Transition constraints: no negative inventory without removal rule, monotonic time unless story explicitly supports time travel, character alive/dead consistency, explicit cause for location change and item ownership; no unknown keys from model output. Effects are authored rules or constrained validated operations.

## Why branching explodes
If each node has b choices for depth d, possible leaves b^d. At b=3,d=10 this is 59,049 leaves, not feasible to author independently. Use **conditional convergence**: branches rejoin scenes but carry consequences in structured state, changing available actions, details and endings. Avoid cosmetically different choices that always converge to the same outcome without consequences.

## MVP algorithm
1. Load canonical published graph version and user run snapshot.
2. Filter permitted choices by deterministic `requires` predicates.
3. Client submits `{choice_id, expected_version, idempotency_key}`.
4. Server begins transaction, looks up prior idempotency receipt, validates owner and state version.
5. Apply transition effects, emit immutable event, bump version, return committed scene.
6. Resolve `scene_audio` in licensed cache. If present, return playback authorization.
7. If dynamic, enqueue job with bounded tokens/characters/cost. Do not block API for unbounded generation.
8. Return pending state plus authorized text/fallback while processing.
9. On success publish generated asset *only to appropriate run/cache scope*, then notify client; on failure mark retryable/nonretryable with remedy.

**Current demo implements steps 1–5 and authorized pre-rendered demo audio in step 6. Nothing from step 7 onward is live.**

## LLM agent pipeline plan
`Planner` receives world bible, explicit structured facts, local summaries and allowed action IDs. Returns JSON plan with source fact references and candidate beat IDs; no free tool execution. `Writer` receives ONLY approved plan, intended audience, genre, length cap, style guide, narration perspective and dialogue rules. `Validator` checks structured facts, entity locations, causality, timeline, references and content safety. `Fallback` returns edited template/approved authored beat or error, never contradiction.

## Long-term memory
- Tier 1: canonical state with exact facts and event hashes; always included/queried deterministically.
- Tier 2: episodic summaries grounded in specific events and provenance; not allowed to overwrite Tier 1.
- Tier 3: recent raw scenes; bounded token window.
- Optional retrieval using embeddings only for relevant authored lore; tag by edition/rights and never ingest unlicensed material.

## Dynamic writing output example (not yet implemented)
```json
{
  "scene_text": "An bước chậm qua hành lang...",
  "speaker_spans": [{"speaker_id":"narrator", "start":0, "end":34}],
  "referenced_event_ids": ["event-0002"],
  "proposed_world_delta": [],
  "narrative_goal": "Reveal information about cellar",
  "age_content_tags": ["suspense"]
}
```

Do not accept this JSON as canonical just because syntactically valid. Enforce schema, byte/char budgets, safety, fact references, speaker/voice permissions, and rights before TTS/render. Use stable ID references and escaped text.

## Specific edge cases
- Double tap or retry during 4G loss (must be idempotent).
- Choice from previous screen/version (must reject 409).
- Player chooses unavailable key/object (must reject).
- Model creates new character and retroactively claims relationship (must block or ask authored rule).
- Generated audio canceled mid-render (must not charge twice or leave invisible story step).
- Licensed source expires while render job pending (cancel generation and media access).
- Concurrent login on two devices (single canonical sequence, conflict resolution UX).
- Old scene references after author editing (pin edition).
- Intentionally user-injected prompt instructions inside free-text choice (treat as story input, never operational instruction).

## Evaluation
Offline benchmark: at least 100 adversarial run trajectories over multiple story seeds, annotated with intended facts; target zero deterministic rule breaks and track contradiction errors per 100 scenes from human judges. Use two independent human reviewers for engagingness/naturalness/choice meaning; report disagreement. Evaluate p50/p95 latency, retries, token cost, provider failover and cache hit. A/B against fixed authored-only branch, not simply between two LLM prompts.

## Research questions (R5)
How to learn a **state-aware writer** from rights-cleared Vietnamese narratives? Does constrained decoding with event-grounded retrieval beat simple world-summary prompts? How to maximize meaningful branch impact under a fixed TTS cost budget? Can a small model distill author-approved beat mapping without increasing contradiction rate? Any LoRA preference model must compare with strong prompt-only baseline, held-out storylines and human ratings.
