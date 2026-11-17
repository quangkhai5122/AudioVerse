# ADR-001: Two modes — fixed licensed audio and authored branching
**Status:** Accepted for starter  **Date:** 2026-11-17

## Context
User wants both legally sourced human audio from the Internet and AI interactive branching. Rights to stream a human recording do not automatically include rights to adapt a story, train voices or create new branches.

## Decision
Implement separate content editions with explicit action permission. Fixed audio never enters narrative generator by default. Interactive originals use graph+state; authorized adaptations may connect only under derivative grants. Share app/player/library, not implicit content rights.

## Alternatives rejected
A single universal ingest-and-generate pipeline (rights and quality failures); only AI TTS library (poor differentiation); fully free-form AI stories (unstable canon, cost uncertainty).

## Consequences
More metadata, rights review and content work, but rights can fail closed and audio pipeline stays understandable. Production requires versioned licenses and a secure rights reviewer.
