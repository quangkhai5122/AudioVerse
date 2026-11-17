# Production infrastructure target and cloud migration gates

## Current
Only loopback FastAPI/SQLite and static local demo media. Flutter source not built. No deployment pipeline, SSL, real auth or cloud account.

## Target initial cloud design (after compliance approval)
- API and internal reviewer web on managed app runtime (Railway/Render/Fly or regional approved equivalent), isolated DB/service credentials.
- Managed PostgreSQL with daily backup, PITR where available, read/write scoped roles and migrations.
- Redis/Valkey or durable managed task queue for LLM/TTS jobs; worker runs with independent scale and global budget.
- Private object storage + authz edge; Cloudflare R2 only if geography/contract/rights allows. Avoid public bucket URLs for paid content.
- Secrets in managed vault, HTTPS and DNS, error monitoring, structured logs, retention and alert channels.
- Separate dev/staging/prod tenants, work/version/rights data migrated via signed artifact release.

## Scaling sequence
Single API + 1 worker -> separate generation worker autoscale -> independent queue/DB tuning -> CDN prefetch and cache -> read replicas/partitioning only after observed saturation. Do not default to Kubernetes.

## Infrastructure as code
Create Terraform/OpenTofu configs only once cloud/provider and legal region decided. Pin runtime/image versions, configuration schemas and rollback. CI should not hold production secrets unless deployment controls and owner approval in place.

## Deployment release gates
Auth, rate limits, encrypted backups, private media, approved content manifest, app-store signed billing, analytics consent, moderation, takedown, Vietnam game/service determination, data protection compliance and incident drills. A local demo environment variable change must never bypass these gates.
