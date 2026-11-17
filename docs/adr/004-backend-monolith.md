# ADR-004: Modular FastAPI backend with Postgres target
**Status:** Accepted for starter **Date:** 2026-11-17

## Decision
FastAPI and Python for API and AI orchestration. Local demo uses SQLite for no-setup tests. Production target PostgreSQL with migrations, separate worker/queue and private object storage. One modular monolith, not immediate microservices/Kubernetes.

## Why
Fast iteration, predictable tests and shared Python AI ecosystem. Distinct domain modules retain later extraction option. SQLite demo not suitable for public multi-user/concurrent deployment, and actor header is not auth.

## Revisit when
Large-scale independent worker saturation, measured DB contention, app/API traffic and staff on-call needs justify splitting services.
