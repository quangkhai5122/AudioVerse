# ADR-002: Deterministic canonical narrative state
**Status:** Accepted for starter **Date:** 2026-11-17

## Decision
Store an authored directed scene graph; choices have typed preconditions and effects. All canonical changes are validated and committed transactionally by server; LLM only drafts text under constraints and cannot mutate facts directly.

## Why
LLMs can contradict prior scenes and invent possessions/character events. Event sourcing+versions support replay and debuggability. The graph can converge conditionally to avoid combinatorial authoring explosion.

## Alternatives
Free-form chat log as state (hard to validate); LLM generates state JSON and auto-writes DB (security/logic errors); every branch pre-authored (unmanageable at scale).

## Cost
More narrative design and eval fixtures. This is a conscious tradeoff for consistency and user trust.
