# AI Coding Agent playbook

## Task loop
Read -> reproduce baseline -> plan minimal changes -> edit with tests -> validate negative cases -> inspect diff -> update docs/state -> report next task. Limit WIP to one major task. Use feature flags and deterministic fixtures.

## Task selection
Pick a READY task with no unmet dependency, unless owner explicitly names a task. If an owner request spans modules, create a task packet with a concise API/compatibility contract and split into sequential PRs. Do not start remote services without credentials and permission.

## Coding requirements
- Python: explicit response schemas, typed data models, tests for errors and permission failures, no silent except.
- Flutter: verify actual SDK, Android/iOS manifest, audio interruptions, process recreation and accessibility.
- DB: version schema and write migrations; audit event immutability; never modify production tables directly.
- LLM: prompts are test inputs, do not infer rights from prompt text; validate JSON with schema; bounded retries.
- Provider costs: record token/character usage, cache hit, cost estimate and provider request id where applicable.
- Content: original or cleared provenance only; unverified media in quarantine; no automatic publish.

## PR/checklist
- Requirements IDs covered and statuses updated?
- Happy + invalid + permission + duplicate + timeout tests?
- No `X-Demo-Actor` or demo content rights flag in public deployment?
- Error handling avoids leaking secrets/PII?
- Existing run/version compatibility checked?
- Updated API/schema/task/log and release gates?

## Useful owner instruction examples
"Read repository state and implement T001 only, run Flutter and Python tests, update log, do not push."
"Review T006 AI design only. Produce benchmark plan and eval fixtures; no paid API calls."
"Audit content permissions on all assets. Report exact missing evidence; do not set any license as verified."
