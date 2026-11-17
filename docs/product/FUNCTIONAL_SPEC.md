# AudioVerse — Complete functional requirements register

**Version:** 2026-11-17 · **Total:** 182 requirements · **Single source of truth:** `requirements.psv`

## Status legend
`DEMO`: executed locally with non-production security; `SOURCE`: code present but build validation pending; `PLANNED`: not implemented; `BLOCKED`: compliance/expert gate; `DONE-PROD`: would require release evidence. No feature is DONE-PROD at present.

Priority P0 means critical to core architecture, not release-ready. P1 commercial MVP after gates, P2 expansion, P3 research. Each acceptance criterion is a minimum; associated task packet must add failure, edge, security and usability tests.

## Coverage summary

| Area | Number |
|---|---:|
| Account | 10 |
| Catalog | 12 |
| Library | 7 |
| Player | 18 |
| Interaction | 18 |
| Narrative AI | 18 |
| Audio/TTS | 16 |
| Rights | 16 |
| Content Studio | 12 |
| Billing | 13 |
| Operations | 13 |
| Security | 15 |
| Recommendation | 7 |
| Localization | 7 |

## Account

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `ACC-01` | P0 | PLANNED | Anonymous browse of free catalog | User can view licensed free work without an account |
| `ACC-02` | P1 | PLANNED | Email/passkey/social login with verified identity | Server binds sessions to the correct user identity |
| `ACC-03` | P1 | PLANNED | Guest-to-account safe migration | Library and runs migrate exactly once |
| `ACC-04` | P1 | PLANNED | Session token refresh and revocation | Revoked session can no longer retrieve private data |
| `ACC-05` | P1 | PLANNED | Device session management | User can revoke individual device sessions |
| `ACC-06` | P1 | PLANNED | Delete account and personal data request | Deletion and retention audit follow documented policy |
| `ACC-07` | P1 | PLANNED | Data export for user | Export contains runs and personal preferences only for owner |
| `ACC-08` | P2 | PLANNED | Optional age gate and parental controls as required | Applicable age restrictions enforced before content access |
| `ACC-09` | P1 | PLANNED | Restore accounts without losing paid rights | Store-verified entitlements survive reinstall |
| `ACC-10` | P1 | PLANNED | Production RBAC for users creators reviewers staff | Role escalation attempts denied and audited |

## Catalog

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `CAT-01` | P0 | DEMO | List demo work with metadata | GET catalog returns authored work without leaking media secrets |
| `CAT-02` | P0 | DEMO | Work title synopsis genre and localization | GET work includes normalized public metadata |
| `CAT-03` | P1 | PLANNED | Separate fixed and interactive editions | Edition includes distinct rights and AI permissions |
| `CAT-04` | P1 | PLANNED | Search by title narrator and tag | Results match indexed content and access policy |
| `CAT-05` | P1 | PLANNED | Content category and mood filters | Query returns only eligible published works |
| `CAT-06` | P1 | PLANNED | Work page with episodes and duration | Metadata matches actual audio sequence |
| `CAT-07` | P1 | PLANNED | Creator credits and verified source label | Listener sees legally appropriate attribution |
| `CAT-08` | P1 | PLANNED | Explicit human versus AI voice labels | Every play screen identifies synthetic narration |
| `CAT-09` | P1 | PLANNED | Published schedule and next episode | Scheduled episode not accessible before release |
| `CAT-10` | P1 | PLANNED | Age and content warnings | Sensitive content filtered according to user settings |
| `CAT-11` | P2 | PLANNED | Editorial featured lists and playlists | Editor changes lists with approval history |
| `CAT-12` | P2 | PLANNED | Multilingual metadata for expansion | Locale fallback never alters canonical original text |

## Library

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `LIB-01` | P0 | PLANNED | Follow work and add/remove to library | Repeated toggles reconcile deterministically |
| `LIB-02` | P1 | PLANNED | Recent listened and continue listening | Resume correct work chapter and position |
| `LIB-03` | P1 | PLANNED | Playlist and saved titles | No duplicate item loss after sync |
| `LIB-04` | P1 | PLANNED | History synced across devices | Server resolves simultaneous playback conflicts |
| `LIB-05` | P1 | PLANNED | Liked and disliked works private by default | Private preferences inaccessible to other users |
| `LIB-06` | P2 | PLANNED | Recommendation explanation | User can inspect why a work was recommended |
| `LIB-07` | P2 | PLANNED | Library categories and reading goals | Private analytics respect opt-out |

## Player

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `PLY-01` | P0 | DEMO | Stream a local MP3 with web native controls | Browser plays original demo media |
| `PLY-02` | P0 | DEMO | Foreground Flutter MP3 scene player source | Flutter analyze widget tests and Android emulator QA passed; iOS requires macOS |
| `PLY-03` | P1 | PLANNED | Background audio lockscreen media controls | Play pause seek work with screen off on devices |
| `PLY-04` | P1 | PLANNED | Chapter navigation and auto-next | No skipped or repeated chapters during transition |
| `PLY-05` | P1 | PLANNED | Playback speed from 0.8x to 2x | Speed consistent after resume |
| `PLY-06` | P1 | PLANNED | Sleep timer and fade out | Playback stops at chosen interval |
| `PLY-07` | P1 | PLANNED | Seek forward/backward increments | Seek requests stay inside audio duration |
| `PLY-08` | P1 | PLANNED | Progress write-back on pause and background | Last committed position survives app restart |
| `PLY-09` | P1 | PLANNED | Reconnect after network loss | Player resumes correct byte range without duplicate billing |
| `PLY-10` | P1 | PLANNED | Authorized offline download | Expired or revoked license prevents new access as required |
| `PLY-11` | P1 | PLANNED | Download queue retry and storage quota | Failed downloads resume without corrupt files |
| `PLY-12` | P1 | PLANNED | Accessible transcript synchronized to time | Timestamped transcript follows current playback |
| `PLY-13` | P1 | PLANNED | Audio focus interruptions | Phone call pause and resume follow platform policy |
| `PLY-14` | P1 | PLANNED | No silent autoplay on opening screen | User initiates playback according to platform policy |
| `PLY-15` | P1 | PLANNED | Protected audio URL with short expiry | Unauthorized request denied including cached expired rights |
| `PLY-16` | P2 | PLANNED | Audio quality network adaptive | Playback remains stable under slow cellular bandwidth |
| `PLY-17` | P2 | PLANNED | Bluetooth and car media integration | Headset controls are usable without touching device |
| `PLY-18` | P2 | PLANNED | Offline episode metadata and transcript | All cached media content stays license-scoped |

## Interaction

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `INT-01` | P0 | DEMO | Create persistent story run | Run id and initial scene are returned |
| `INT-02` | P0 | DEMO | Display 2 or more authored choices | Options depend on canonical state prerequisites |
| `INT-03` | P0 | DEMO | Apply deterministic transition and effects | Expected flag changes appear and wrong choices denied |
| `INT-04` | P0 | DEMO | Append choice event to SQLite | Events are ordered and persist between API requests |
| `INT-05` | P0 | DEMO | Idempotent replay with immutable result | Repeated key does not create second event |
| `INT-06` | P0 | DEMO | Reject stale story run versions | Version conflict returns 409 without rewriting history |
| `INT-07` | P0 | DEMO | Three sample endings with visible divergence | Author graph test reaches three distinct endings |
| `INT-08` | P1 | PLANNED | Run tied to immutable story edition version | Old run remains valid after new edition publication |
| `INT-09` | P1 | PLANNED | Passive authored default at each decision | Listening can continue without mandatory prompts |
| `INT-10` | P1 | PLANNED | Open-text player actions with constrained intent | LLM output cannot bypass allowed action grammar |
| `INT-11` | P1 | PLANNED | Meaningful choice consequences beyond text style | State changes are reflected in later gated scenes |
| `INT-12` | P1 | PLANNED | Run resume after app crash and device switch | Player returns exact committed scene and position |
| `INT-13` | P1 | PLANNED | Versioned run rewind or restart | No accidental corruption of previous route |
| `INT-14` | P1 | PLANNED | Branch generation progress and cancellability | Cancelled jobs not billed twice |
| `INT-15` | P2 | PLANNED | Share safe non-spoiler branch summary | Private run details not published without consent |
| `INT-16` | P2 | PLANNED | Voice-command input for story choices | ASR privacy and safe disambiguation tested |
| `INT-17` | P2 | PLANNED | Choice replay and what-if endings | Replay produces new run without changing past records |
| `INT-18` | P1 | PLANNED | Story state snapshot recovery | Deterministic replay yields identical state after restore |

## Narrative AI

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `NAR-01` | P0 | DEMO | Deterministic non-generative narration provider contract | Demo uses no paid inference and cannot mutate state |
| `NAR-02` | P1 | PLANNED | Swappable LLM provider adapters | Provider failing triggers controlled fallback |
| `NAR-03` | P1 | PLANNED | Canonical character world and rules | Canonical facts are validated before scene write |
| `NAR-04` | P1 | PLANNED | Scene planner output strict schema | Invalid fields are rejected not silently trusted |
| `NAR-05` | P1 | PLANNED | Narration writer with Vietnamese style guides | Output follows target length register and character voice |
| `NAR-06` | P1 | PLANNED | Deterministic world state validation | Contradictions block commit |
| `NAR-07` | P1 | PLANNED | Episodic memory and recent context retrieval | Relevant past events recovered by cited event ids |
| `NAR-08` | P1 | PLANNED | Model prompt version and provider usage logs | Each output traceable to version and cost |
| `NAR-09` | P1 | PLANNED | Generation budget token and cost caps | Unbounded retries cannot exhaust budget |
| `NAR-10` | P1 | PLANNED | Prompt injection defense on imported text | Story text cannot issue tool or system instructions |
| `NAR-11` | P1 | PLANNED | Safety moderation and age rating gate | Blocked output never published as audio |
| `NAR-12` | P1 | PLANNED | Retry and safe authored fallback | Provider outage cannot corrupt run |
| `NAR-13` | P2 | PLANNED | Meaningful branch impact evaluator | Human review and test metrics detect cosmetic choices |
| `NAR-14` | P2 | PLANNED | SFT/LoRA optional style adapter | Fine-tuning must beat prompt baseline and be licensed |
| `NAR-15` | P2 | PLANNED | Pairwise preference evaluation | Quality changes validated on held-out blinded stories |
| `NAR-16` | P2 | PLANNED | Controlled narrative memory compression | Summary does not erase canonical evidence |
| `NAR-17` | P2 | PLANNED | Narrative diversity without plot contradiction | Variation bounded to presentation not canon |
| `NAR-18` | P2 | PLANNED | Model audit and rollback | New provider version can be rolled back per story |

## Audio/TTS

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `TTS-01` | P0 | DEMO | Original demo MP3s created by local TTS | 11 synthetic files playable from original script |
| `TTS-02` | P1 | PLANNED | Cloud TTS provider adapter interface | API output normalized with checksum and metadata |
| `TTS-03` | P1 | PLANNED | Provider selection per voice language and cost | Routing logs cost and fallback decision |
| `TTS-04` | P1 | PLANNED | Pronunciation dictionary for Vietnamese names | Proper names read consistently across chapters |
| `TTS-05` | P1 | PLANNED | Human narrator audio ingestion with QC | Uploaded file remains quarantined until licensed and reviewed |
| `TTS-06` | P1 | PLANNED | Loudness normalization and codec transcode | Output conforms to publishing preset and manifests |
| `TTS-07` | P1 | PLANNED | Transcript and scene alignment | Correct text audio segment mapping saved |
| `TTS-08` | P1 | PLANNED | Pre-render authored branch clips | Prepared clip can play without LLM call |
| `TTS-09` | P1 | PLANNED | Audio synthesis job queue and retry | Idempotent render jobs avoid duplicate charges |
| `TTS-10` | P1 | PLANNED | Cache matching same rights version and text | No cross-user leak of private generated content |
| `TTS-11` | P1 | PLANNED | TTS first-audio latency measurement | Provider p50 p95 recorded per length and locale |
| `TTS-12` | P1 | PLANNED | Audio provenance and model version metadata | Every released audio linked to rights and model |
| `TTS-13` | P2 | PLANNED | Optional multi-speaker playback | Speaker attribution correct through scene sequence |
| `TTS-14` | P2 | PLANNED | Consent-gated voice cloning research | No sample accepted without chain of consent and training right |
| `TTS-15` | P2 | PLANNED | Licensed self-host TTS experiments | Weights data and output license audits pass |
| `TTS-16` | P2 | PLANNED | Expressiveness listener evaluation | Blinded Vietnamese evaluation measures preference |

## Rights

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `RGT-01` | P0 | DEMO | Fail-closed demo stream and derivative action checks | Unlisted rights rejected by code and unit test |
| `RGT-02` | P0 | PLANNED | Canonical chain of title for text and translation | Legal reviewer can verify underlying work ownership |
| `RGT-03` | P0 | PLANNED | Separate performance master voice and AI-use rights | Missing one applicable grant blocks action |
| `RGT-04` | P0 | PLANNED | Versioned contract evidence reference | No self-approval from creator submitted metadata |
| `RGT-05` | P0 | PLANNED | Rights by territory language time and edition | Out-of-scope delivery denied with auditable reason |
| `RGT-06` | P0 | PLANNED | Derivative use action gate | Stream-only grant cannot enter branching system |
| `RGT-07` | P0 | PLANNED | Voice cloning consent gate | Unauthorized voice embedding or fine-tuning denied |
| `RGT-08` | P1 | PLANNED | License expiration and renewal alerts | Expired content unpublished or revalidated as required |
| `RGT-09` | P1 | PLANNED | Takedown freeze of new downloads and generation | Takedown changes effective permissions rapidly |
| `RGT-10` | P1 | PLANNED | Evidence and approval audit log | Reviewer identity timestamp decision append-only |
| `RGT-11` | P1 | PLANNED | Contractual creator credit and attribution | Credits meet terms across mobile and web |
| `RGT-12` | P1 | PLANNED | Specific right to offline listening | App does not enable downloads under stream-only grant |
| `RGT-13` | P1 | PLANNED | Third-party API and platform terms registry | Do not rehost YouTube or bypass protected audio |
| `RGT-14` | P1 | PLANNED | Human escalation for disputed claims | Disputed work paused until review |
| `RGT-15` | P2 | PLANNED | Creator royalty contract version registry | Payout calculations trace to active agreement |
| `RGT-16` | P2 | PLANNED | Provider output/weight training rights review | Licenses checked for commercial inference and adaptation |

## Content Studio

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `CMS-01` | P1 | PLANNED | Creator and reviewer invitation workflow | Distinct roles and approvals enforced |
| `CMS-02` | P1 | PLANNED | Work metadata and edition editor | Draft publish state explicit and versioned |
| `CMS-03` | P1 | PLANNED | Episode and scene graph editor | Author validates nodes edges reachability and endings |
| `CMS-04` | P1 | PLANNED | Story world/character bible editor | Changes require versioning and review |
| `CMS-05` | P1 | PLANNED | Secure audio and transcript upload | Quota file type checksum malware checks |
| `CMS-06` | P1 | PLANNED | Technical audio QC and preview | Waveform duration clipping checked before publish |
| `CMS-07` | P1 | PLANNED | Rights and age content review workflow | Cannot publish without approval gates |
| `CMS-08` | P1 | PLANNED | Episode scheduling and unpublishing | Publication times and rights windows respected |
| `CMS-09` | P1 | PLANNED | Rollback published edition | Existing listeners retain compatible run versions |
| `CMS-10` | P1 | PLANNED | Creator performance dashboard | Only authorized statistics shown |
| `CMS-11` | P2 | PLANNED | Narrative quality editorial review queues | Editors approve scene generations for fixed library |
| `CMS-12` | P2 | PLANNED | Multiple staff reviewer roles | Separation of duties enforced and audited |

## Billing

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `BIL-01` | P1 | PLANNED | Native Google Play subscription integration | Server verifies purchase token and app signature |
| `BIL-02` | P1 | PLANNED | Apple IAP subscription integration | Server validates transaction and renewal lifecycle |
| `BIL-03` | P1 | PLANNED | Server-side entitlement authorization | Client cannot grant premium by changing local state |
| `BIL-04` | P1 | PLANNED | Restore purchases across devices | Store receipts reconcile idempotently |
| `BIL-05` | P1 | PLANNED | Free preview content policy | Preview length and quota clear to users |
| `BIL-06` | P1 | PLANNED | Separate passive and interactive limits | Compute quota measurable before generation |
| `BIL-07` | P1 | PLANNED | Atomic spend ledger for AI jobs | Duplicate requests cannot debit twice |
| `BIL-08` | P1 | PLANNED | Cost guardrail and per-user ceiling | Provider stop cannot exceed configured monthly budget |
| `BIL-09` | P1 | PLANNED | Refund and entitlement revocation handling | Reversed transaction reflected in server rights |
| `BIL-10` | P1 | PLANNED | Transparent renew and cancel terms | No hidden renewal or misleading coin balance |
| `BIL-11` | P2 | PLANNED | Story/season purchase and bundle offers | User sees exact unlocked content and duration |
| `BIL-12` | P2 | PLANNED | Creator royalty calculation | Statements reconcile with net receipts and contracts |
| `BIL-13` | P2 | PLANNED | Multi-currency tax reporting integration | Export reconciles store reports and financial books |

## Operations

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `OPS-01` | P1 | PLANNED | App crash and playback diagnostics | Crash-free session rate measured by platform and release |
| `OPS-02` | P1 | PLANNED | Narrative contradiction and validation rate | Failed samples linked to prompt and run version |
| `OPS-03` | P1 | PLANNED | Provider time and response error dashboard | p50 p95 AI and audio generation durations tracked |
| `OPS-04` | P1 | PLANNED | AI cost ledger per provider and user segment | Costs calculated from captured actual billable units |
| `OPS-05` | P1 | PLANNED | Content performance funnel | Chapter-to-chapter continuation measured by cohort |
| `OPS-06` | P1 | PLANNED | D1 D7 D30 and paying retention analysis | Metrics defined by registered cohort denominator |
| `OPS-07` | P1 | PLANNED | App feature kill switch | Can disable remote generation without app release |
| `OPS-08` | P1 | PLANNED | Incident alerts and pager path | On-call runbook identifies severity and response |
| `OPS-09` | P1 | PLANNED | Backup and restore drill | Recovery meets explicit RPO RTO test |
| `OPS-10` | P1 | PLANNED | User feedback support queue | User can report audio broken or content violation |
| `OPS-11` | P1 | PLANNED | Staged rollout and rollback | Failed release rolls back without data loss |
| `OPS-12` | P2 | PLANNED | AI A/B evaluation flags | Assigned variant is stable and privacy aware |
| `OPS-13` | P2 | PLANNED | Creator content abuse moderation dashboard | Repeat offender workflows and appeals auditable |

## Security

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `SEC-01` | P0 | PLANNED | Production authentication beyond demo actor | Unauthenticated run access denied |
| `SEC-02` | P0 | PLANNED | Authorization on every private resource | User A cannot read user B story history |
| `SEC-03` | P0 | PLANNED | HTTPS end to end and secure tokens | No cleartext credentials in production logs |
| `SEC-04` | P0 | PLANNED | Storage encryption and backups | Secrets and PII protected under tested key policy |
| `SEC-05` | P0 | PLANNED | Untrusted story text prompt injection boundary | Imported metadata cannot issue system instructions |
| `SEC-06` | P0 | PLANNED | Data minimization and retention schedule | No unnecessary raw voice recordings retained |
| `SEC-07` | P1 | PLANNED | Privacy notice and deletion workflow | User consent rights data access actionable |
| `SEC-08` | P1 | PLANNED | API rate limit and abuse detection | Attack traffic throttled without blocking normal users |
| `SEC-09` | P1 | PLANNED | Media entitlement and short signed URLs | Expired subscription cannot mint access URLs |
| `SEC-10` | P1 | PLANNED | Secret management and rotation | No API secrets bundled into mobile clients |
| `SEC-11` | P1 | PLANNED | Security headers and mobile certificate controls | Critical traffic protected and audited |
| `SEC-12` | P1 | PLANNED | Tamper evident event and reviewer audit | Published decisions attributable to authorized reviewers |
| `SEC-13` | P1 | PLANNED | Offboarding and privileged access review | Staff deprovisioning revokes content access quickly |
| `SEC-14` | P1 | PLANNED | Backup recovery and multi-tenant isolation tests | Data loss or cross-tenant leak tests block release |
| `SEC-15` | P1 | PLANNED | Content moderation and user reporting | Harmful unreviewed public stories cannot publish |

## Recommendation

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `REC-01` | P2 | PLANNED | Editorial mood and genre matching | Relevant content can be discovered without private profiling |
| `REC-02` | P2 | PLANNED | Continue-next and series following | Episode availability triggers accurate next recommendation |
| `REC-03` | P2 | PLANNED | Privacy-aware behavioral ranking | Opt out users still get coherent discovery |
| `REC-04` | P2 | PLANNED | Diversity and newcomer exposure | Feed does not collapse to one popular creator |
| `REC-05` | P2 | PLANNED | Explore-exploit experiment framework | Ranking evaluated on completion not raw clicks |
| `REC-06` | P2 | PLANNED | Content age and rights filter before ranking | Never recommends unavailable or restricted audio |
| `REC-07` | P2 | PLANNED | Personalized listening history summaries | Data surfaced only to its account owner |

## Localization

| ID | Priority | Status | Behavior | Acceptance criterion |
|---|---|---|---|---|
| `LOC-01` | P1 | PLANNED | Vietnamese UX and narrator labels | All core text supports native Vietnamese typography |
| `LOC-02` | P1 | PLANNED | Vietnamese place and name pronunciation dictionary | TTS QA catches common Sino-Vietnamese misreadings |
| `LOC-03` | P1 | PLANNED | Low bandwidth listening preset | Player supports compressed audio and retry |
| `LOC-04` | P1 | PLANNED | Android-first device coverage study | Tests midrange devices and mobile data |
| `LOC-05` | P1 | PLANNED | Content policy for Vietnamese local regulations | Reviewer signs age/rating and applicable publication category |
| `LOC-06` | P2 | PLANNED | Voice/accent preference under license | User can select authorized narrators where available |
| `LOC-07` | P2 | PLANNED | Translation/foreign distribution rights | No translated derivatives without a separate right grant |

## Definition of done for any item

1. Product owner accepts behavior and content rights; risk classification recorded.
2. API/client behavior and schema written in versioned documents or OpenAPI.
3. Unit and integration tests cover positive, failure, concurrency and access cases.
4. Agent updates task packet, ADR if needed, PROJECT_STATE, CURRENT_TASK, SESSION_LOG and this register.
5. Verified execution evidence attached; unrun Flutter/browser/device tests remain pending.
6. Production designation requires compliance, security and release gates in addition to feature tests.
