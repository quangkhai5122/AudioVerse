# Product decisions and unresolved assumptions

## Explicit owner intent from discussion
- AudioVerse targets Vietnamese consumers first.
- Combine licensed human-narrated audio from Internet creators with AI-produced audio.
- Interactive branching by AI is central to differentiation.
- Prepare full architecture, cost study, future fine-tuning options and long-lived AI Agent coding workflow.

## Owner-confirmed engineering protocol — 2026-11-17 (updated 2026-11-18)
- First takeover session: T000 repository onboarding/audit, environment/tests, documentation synchronization, then initial commit/push if Git checks are safe. T001 was subsequently implemented, verified on Android 15 Emulator and Web preview, and approved by owner on 2026-11-18.
- Future sessions start from repository instructions/state/tasks and actual Git/code/test evidence. A request to continue means the highest-priority unfinished task in the approved backlog.
- **Direct `main` branch workflow (2026-11-18):** Merge verified T000/T001 work into `main`. From T002 onward, develop ordinary scoped tasks directly on `main` and commit/push to `origin/main` when tests pass, instead of creating a new branch per milestone (`T001`, `T002`, etc.). No force-push, branch deletion, shared-history rewrite or overwriting others' work. Large/risky/unapproved changes still use an isolated branch before integration.
- This permission does not approve deployment, commercial release, content publication, external messaging, API spending, purchases, billing, legal terms or any rights/legal signoff.
- Close every session with durable state/task/backlog/log updates and a Vietnamese eight-part report. Persist unresolved work and decisions so a new agent needs no prior conversation.

## Design proposals (NOT yet owner-signed contractual commitments)
- Flutter mobile; FastAPI modular monolith; Postgres production; R2/secure media delivery; API-first model benchmarking.
- Originals first for interactive mode; external narrated recordings need itemized rights.
- Initial genre mystery/thriller; passive listening as default with optional choices.
- Budget-based paid AI generation with pre-render/caching; no unlimited personalized narration at low flat fee.
- Free + premium + measured AI quota: pricing subject to user experiment and app-store/legal review.

## Open decisions requiring owner/expert input
D001: Interactive mode classification under VN online-game regulations. D002: First content partners and owner/producer/license evidence. D003: Age group and content policy. D004: Pricing and entitlement structure. D005: Cloud region and local data requirements. D006: Real voice cloning: only if strong economic need and contractual consent. D007: Analytics privacy and data retention period. D008: Publishing entity, terms and creator payout tax status.

Agent must never turn a proposal into "owner approved" silently.
