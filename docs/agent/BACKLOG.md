# BACKLOG — canonical high-level order

| ID | Task | Stage | State | Dependency | Gate |
|---|---|---|---|---|---|
| T000 | Repository onboarding/audit and long-term workflow | R0 | DONE | Local audit evidence | Audit; no production acceptance |
| T001 | Native Flutter build, test and foreground player | R1 | DONE (Android; iOS needs macOS) | Flutter 3.50.0 + Android SDK 36/AVD 35 verified | Device QA (Android pass) |
| T002 | Content rights schema, contract and evidence review design | R1 | DONE | None | Legal rights (schema & policy pass) |
| T003 | Postgres, migrations, user auth and tenant isolation design | R1 | DONE | T002 schema (done); T001 client contract (done) | Security (auth, RBAC & migrations pass) |
| T004 | Authenticated media streaming and signed delivery | R1 | READY | T002 (done), T003 (done) | Rights + security |
| T005 | Player lifecycle, offline/resume/background plan | R1 | PLANNED | T001 (done), T004 | Platform |
| T006 | Narrative AI provider adapters & schema verifier | R2 | READY | T002 (done), narrative eval design | Content rights |
| T007 | TTS API adapters + benchmark & audio pipeline | R2 | READY | T002 (done) | Voice license |
| T008 | Authoring CMS and content publishing gate | R2 | READY | T002 (done), T003 (done) | Provenance review |
| T009 | Story state versioning, branching editor & migrations | R2 | PLANNED | T003 (done), T006 | Narrative QA |
| T010 | Analytics, cost ledger, provider circuit breaker | R2 | PLANNED | T006,T007 | Budget cap |
| T011 | In-app purchase, entitlement and creator royalties | R3 | BLOCKED | T003,T004,T010, legal review | Payments, compliance |
| T012 | Security, privacy, app store and VN game/service review | R3 | BLOCKED | T002-T011 | External expert approval |
| T013 | Beta with authorized stories and curated reviewers | R3 | BLOCKED | T012 | Product release |
| T014 | Commercial launch reliability/incident drills | R4 | BLOCKED | T013 | Launch readiness |
| T015 | Licensed voice fine-tuning experimental program | R5 | DEFERRED | T007 data & licensing | Research |
| T016 | Creator marketplace / self-publishing / moderation | R5 | DEFERRED | T008,T012 | UGC/royalty law |

Definitions: READY = can start locally; PLANNED = awaits prerequisites; BLOCKED = do not proceed without owner/expert signoff; DEFERRED = research backlog. Never mark DONE without automated and/or manual evidence.

## Audit follow-ups — 2026-11-17
- T001 remains next priority; toolchain blockage is an environment prerequisite, resolvable through ordinary local setup. Android-first; iOS needs macOS/Xcode. Extend the existing widget smoke with a fake API and test foreground failure/retry recovery.
- T000 repaired the existing lint gate (8 E701 + 7 I001) and excludes generated egg-info from Git. Full local Ruff passes; one Starlette/httpx warning remains. Dependency versions are captured in the audit; Windows/Python 3.13 and Ubuntu/Python 3.11 CI remain distinct evidence.
- T001/T005: clients do not persist uncertain commands or reconcile committed choices with failed audio loads; Flutter lacks persistent run/position recovery. Web render can overwrite errors. Static findings need regression coverage in their owning tasks.
- T002: expiry/territory/takedown/evidence/approver checks; verified_for_demo is not commercial approval.
- T003/T009: events lack DB immutability/restore replay; runs lack immutable editions. Protect old runs before content edits.
- T003/T004: spoofable actor, public sample media, missing rate limits/response schemas and host override remain demo boundaries.

Audit labels use DONE/PARTIAL/PLANNED/BLOCKED; READY/DEFERRED are queue hints. Toolchain BLOCKED can be resolved by setup; legal/public-release BLOCKED still requires expert/owner gates. Do not infer completion percentages from requirement counts.
