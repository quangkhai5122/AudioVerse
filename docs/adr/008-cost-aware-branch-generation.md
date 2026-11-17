# ADR-008: Pre-render > cached > bounded on-demand generation
**Status:** Proposed for commercial design **Date:** 2026-11-17

## Context
One hour private AI narration can cost as much as the net contribution from a low-price monthly subscriber. High variance in AI branching makes unlimited use financially unsafe.

## Decision proposal
Most public scenes pre-render, common branches cached within rights scope, dynamic variant only if meaningful and budgeted. Prompt length, max scene, retry count and TTS char count bounded per run/plan. Trial users receive a small measurable quota; not an unlimited plan.

## Revisit
Run R2 cache effectiveness and p95 time-to-audible benchmark before monetization. No rollout without cost ledger.
