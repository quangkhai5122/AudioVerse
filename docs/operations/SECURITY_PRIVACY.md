# Security, privacy and adversarial risks

## Important current limitations
The demo is **not safe on public networks**. `X-Demo-Actor` can be impersonated, sample audio is public, SQLite runs live on local disk, there is no RBAC, TLS, rate limiting, secure media tokens or authenticated reviewer. No production deployment or real user data is permitted.

## Sensitive assets
Account identity/contact, voice recordings and transcripts, play history and inferred preferences, creator agreement and personal payment information, unpublished stories, model prompts/outputs, API and storage credentials, store transaction identifiers and customer support messages.

## STRIDE-style risks and controls
| Threat | Example | Production mitigation |
|---|---|---|
| Spoofing | Another user reads story run | OIDC/user auth with server-side resource authorization |
| Tampering | Client changes version/canon or payment | Signed store verification, optimistic DB transaction, append-only events |
| Repudiation | Reviewer denies approval | Immutable audit with actor, timestamp, evidence hash |
| Information disclosure | Public URL leaks private generated audio | Scoped signed media access, short TTL, object bucket private |
| Denial of service | Infinite LLM/TTS queue | Quota, rate limits, global budget ceilings, circuit breaker |
| Elevation of privilege | Creator approves own license | Separation of duties RBAC + workflow guard |
| Prompt injection | Story transcript asks agent to reveal secrets | Untrusted data boundary, no direct tool access from writer, strict output schema |
| Rights abuse | Internet link used as proof | Rights evidence review per work/recording/voice |
| Model abuse | Voice cloning identifiable person | Explicit consent and separate restricted pipeline |
| Cache cross-leak | Shared generated user branch | Private cache namespace, no unapproved sharing |

## Controls for production
- HTTPS-only, HSTS where appropriate; short-lived access tokens, refresh rotation, cookie/CSRF rules where relevant; secure OS keystore for device tokens.
- Object storage encryption, KMS-managed keys, key rotation, least-privilege IAM, secrets not shipped in Flutter, anti-malware input controls.
- Per-user and per-provider rate limits and budget; request-id and audit logs without unredacted personal audio/transcripts.
- Data minimization, privacy notice, retention and deletion schedule, purpose-specific consent for voice/analytics; age protections where required.
- Authz tests on every endpoint; defense against path traversal and SSRF on any external URL ingestion; signed webhooks for billing/creator payments.
- Recovery drill: automated backups with encryption, restore on staging, documented RPO/RTO and incident response escalation.

## Security test gates
1. Unauthorized access user A->B blocked across runs/media/billing.
2. Unlicensed derivative and voice operation fail closed.
3. Replay attack on payment and story choice returns same receipt, no double debit.
4. Hostile story text and URL metadata cannot override system instructions or trigger network access.
5. Media URL expiry, rights revocation and logout are honored at renewal points.
6. Privacy delete/export requests cover DB, logs, audio queue and backups according to lawful retention policy.
7. Security review and external penetration test or equivalent review before wider commercial launch.

## Vietnam legal note
Privacy requirements under Law 91/2025/QH15 and implementing instruments need a qualified compliance review. AudioVerse may involve profiling of reading interests and ASR voice data; these are not just technical telemetry. See legal release gates for additional game/service classification.
