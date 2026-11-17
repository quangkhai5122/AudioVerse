# ADR-006: Explicit production security and legal cutover
**Status:** Accepted for starter **Date:** 2026-11-17

## Decision
A local demo mode is intentionally isolated. It contains a spoofable demo actor header, unprotected synthetic MP3, SQLite and unverified production rights review. Code explicitly disallows env != demo and defaults to loopback. There is no production flag to flip.

## Rationale
Avoid accidental exposure of user story state or unauthorized content during early research. Public app requires new real authentication, appropriate Vietnam game/service permits, secure billing/media, privacy controls and content contracts.

## Consequences
A future separate deployment profile is a dedicated security project requiring QA and expert signoff, not a one-line configuration change.
