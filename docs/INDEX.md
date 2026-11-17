# Complete documentation index

## For owner
- `01_TONG_QUAN_VIET_NAM.md` — Executive guide in Vietnamese.
- `00_START_HERE.md` — Product constitution and implementation truth table.
- `product/PRD.md` — Scope, audience, growth and product-market fit.
- `product/FUNCTIONAL_SPEC.md` — 182 functional requirements with IDs, status and acceptance.
- `product/UX_JOURNEYS.md` — Journeys, UI screens, error states, accessibility.
- `product/COMPETITOR_MAP.md` — Research evidence and positioning hypotheses.
- `finance/COST_MODEL.md` — Architecture-related unit economics and formulas.
- `finance/BUSINESS_VALIDATION.md` — Research and conversion experiments.

## For engineering
- `engineering/ARCHITECTURE.md` — Context, components, deployment boundary, SLIs.
- `engineering/API.md` — Implemented routes and target contracts.
- `engineering/DATA_MODEL.md` — Current SQLite and future Postgres schema.
- `engineering/NARRATIVE_ENGINE.md` — Graph/state/LLM planning and evaluation.
- `engineering/AI_EVALUATION.md` — Model benchmark program.
- `engineering/AUDIO_TTS.md` — Human/AI voice, pipeline and license concerns.
- `engineering/FLUTTER_CLIENT.md` — Mobile UI, native player and device QA.
- `engineering/MEDIA_DELIVERY.md` — Rights-protected stream and offline design.
- `engineering/PAYMENTS.md` — IAP, entitlements and quota accounting.
- `engineering/OBSERVABILITY.md` — Events, cost ledger and alerts.
- `engineering/DEPLOYMENT.md` — Staging/prod cloud target and gates.
- `research/RESEARCH_AGENDA.md` — Long-term AI research tracks.
- `research/TECH_SOURCES.md` — Primary reference links for version checks.

## For legal/operations
- `operations/LEGAL_RIGHTS_RELEASE_GATES.md` — Rights chain, Vietnam classification, legal release criteria.
- `operations/CONTENT_PIPELINE.md` — Creator ingest, QA, approvals and takedown.
- `operations/CONTENT_SAFETY.md` — Moderation and age classification.
- `operations/SECURITY_PRIVACY.md` — Threats and production controls.
- `operations/TEST_STRATEGY.md` — Test layers, release requirements.
- `operations/RELEASE_RUNBOOK.md` — Local environment, incidents and release plan.

## For Coding Agents
- `/AGENTS.md` — Mandatory agent operating rules.
- `agent/PROJECT_STATE.md` — Current confirmed implementation and blockers.
- `agent/ONBOARDING_AUDIT_20261117.md` — Takeover audit, executable evidence, environment and discrepancies.
- `agent/CURRENT_TASK.md` — Exactly one active task.
- `agent/BACKLOG.md` — Dependencies, priorities and stages.
- `agent/SESSION_LOG.md` — Durable session history.
- `agent/HANDOFF_PROTOCOL.md` — Compaction and cross-account continuation.
- `agent/AGENT_PLAYBOOK.md` — Code and review workflow.
- `agent/OWNER_DECISIONS.md` — Explicit intent versus proposals.
- `agent/TASK_TEMPLATE.md` — Template for new tasks.
- `tasks/T000_REPOSITORY_ONBOARDING.md`, `tasks/T001...T016` — Audit and engineering task packets, first command and acceptance.
- `adr/001...008` — Architecture decision records and rejected alternatives.

## Single source of truth conflicts
Requirement source is `product/requirements.psv`; generated human-readable Markdown is `product/FUNCTIONAL_SPEC.md`. Run `python scripts/build_requirements.py` after editing PSV. Current functionality is defined by executable code/tests, not future acceptance descriptions. Consult `PROJECT_STATE.md` before claiming deployment readiness.
