# API contract — demo and production target

## General conventions
Base `/api/v1`; JSON UTF-8; IDs opaque. Mutations require idempotency keys and optimistic version where appropriate. In production: `Authorization: Bearer <access_token>`, authz on every private entity, throttling and request trace ID. **Current demo uses `X-Demo-Actor: demo-local` instead; this header is not authentication and must never be trusted in a real deployment.**

## Implemented demo routes

| Method | Path | Request | Response/status | Notes |
|---|---|---|---|---|
| GET | `/healthz` | none | 200 `{status:ok,environment:demo,ai:disabled,billing:disabled}` | Local only |
| GET | `/api/v1/catalog` | none | 200 work list | Anonymous browse allowed (`ACC-01`); includes `edition_id`, `attribution`, `voice_label` |
| GET | `/api/v1/works/{story_id}` | id | 200/404 | Public metadata + attribution |
| GET | `/api/v1/works/{story_id}/rights` | id | 200/404 | Public provenance summary (`RightsGrant` state, territories, languages, renewal alert, asset count) |
| POST | `/api/v1/auth/register` | `{email,password,display_name,device_name}` | 201 `{user,session_id,access_token,refresh_token}` | Creates `listener` account & device session (`ACC-02`) |
| POST | `/api/v1/auth/login` | `{email,password,device_name}` | 200 `{user,session_id,access_token,refresh_token}` or 401 | Scrypt verified login (`ACC-02`) |
| POST | `/api/v1/auth/refresh` | `{session_id,refresh_token}` | 200 rotated tokens or 401 | Rotates `access_jti` & `refresh_token`; replay revokes session (`ACC-04`) |
| POST | `/api/v1/auth/logout` | `Bearer <token>` | 200 `{status:revoked}` | Revokes current device session (`ACC-04`) |
| GET | `/api/v1/me/devices` | `Bearer <token>` | 200 session list | Lists user device sessions (`ACC-05`) |
| DELETE | `/api/v1/me/devices/{session_id}` | `Bearer <token>` | 200/404 | Revokes target device session (`ACC-05`) |
| POST | `/api/v1/me/migrate-guest` | `{guest_actor}` + `Bearer <token>` | 200/409 | Idempotent one-time guest-to-account migration (`ACC-03`) |
| GET | `/api/v1/me/export` | `Bearer <token>` | 200 export bundle | Owner-only personal data, sessions, runs & events export (`ACC-07`) |
| DELETE | `/api/v1/me` | `Bearer <token>` | 200 deletion receipt | Revokes sessions, anonymizes runs, deletes PII (`ACC-06`, `SEC-07`) |
| GET | `/api/v1/admin/security-audit` | `Bearer <token>` | 200/403 | Staff RBAC (`legal_reviewer`/`rights_officer`/`compliance_admin`); logs escalation attempts (`ACC-10`, `SEC-12`) |
| POST | `/api/v1/runs` | `{"story_id":"ben-kia-canh-cua"}` | 201 run snapshot; 401/403 | Pins `edition_id` & `state_checksum` (`INT-08`) |
| GET | `/api/v1/runs/{run_id}` | `Bearer` or demo header | 200/401/404 snapshot | Strictly isolated to owner (`SEC-02`) |
| POST | `/api/v1/runs/{run_id}/choices` | body below | 200 snapshot; 409 stale/reuse; 422 invalid; 401/403/404 | Commits chained `event_hash` & snapshot |
| GET | `/api/v1/runs/{run_id}/events` | `Bearer` or demo header | 200 event list | Ordered, includes `event_hash` |
| POST | `/api/v1/runs/{run_id}/restore` | `Bearer` or demo header | 200 restored snapshot; 409 tamper; 404 | Deterministic event replay & hash verification (`INT-18`) |
| GET | `/api/v1/audio/{scene_id}.mp3` | scene | 200 audio; 403 if stream right/asset quarantined; 404 | Per-scene `AssetLicense` & `stream` gate; demo sample media |
| GET | `/` | none | 200 HTML | Browser demo |

### POST choice example
```json
{
  "choice_id": "follow-tracks",
  "expected_version": 0,
  "idempotency_key": "f77fda344c434ccb90d1d4b69de8a717"
}
```

### Run snapshot response shape
```json
{
  "run_id": "opaque-uuid",
  "story_id": "ben-kia-canh-cua",
  "version": 1,
  "flags": {"saw_tracks": true},
  "scene": {
    "id": "s1", "title": "Trong kho thiết bị",
    "text": "...", "memory_notes": [],
    "choices": [{"id": "take-key", "label": "Giữ chìa khóa B"}],
    "ending": false
  }
}
```

Choice replay with same key/choice returns the original snapshot even if later transitions have happened; reused key with different choice returns 409. Concurrent stale versions return 409 and require client refresh. Preconditions are evaluated by server, not by hiding buttons alone.

## Planned authenticated production endpoints (NOT implemented)

| Domain | Suggested paths | Security requirement |
|---|---|---|
| Identity | `/auth/*`, `/me`, `/me/devices` | OAuth/OIDC, rotation, revocation |
| Catalog | `/works`, `/works/{id}/editions`, `/episodes` | Visibility, territory, age + publish window |
| Playback | `/playback/authorize`, `/progress`, `/downloads` | Signed scoped URL, entitlement, rate limit |
| Interactive | `/runs`, `/runs/{id}/choices`, `/runs/{id}/render`, `/runs/{id}/events` | Optimistic version, cost cap, owner auth |
| AI jobs | `/generations/{job_id}` | Job owner, version, rights and billing |
| Billing | `/billing/offerings`, `/billing/restore`, `/billing/events` | Store signature verification, replay prevention |
| Creator | `/creator/works`, `/creator/assets` | Creator RBAC and antivirus scan |
| Rights | `/admin/rights/{id}/review`, `/admin/takedowns` | Dual-control workflow and append-only audit |
| Observability | `/admin/cost-ledger`, `/admin/incidents` | Staff-only with least privilege |

## Error model for production
Use `{error:{code,message,request_id,retryable}}` (planned), not stack traces. Important codes: `RIGHTS_NOT_GRANTED`, `LICENSE_EXPIRED`, `CONTENT_NOT_AVAILABLE`, `PAYMENT_REQUIRED`, `QUOTA_EXCEEDED`, `STORY_VERSION_CONFLICT`, `GENERATION_PENDING`, `PROVIDER_TIMEOUT`, `MODERATION_BLOCK`, `UNAUTHORIZED`. Current demo uses FastAPI default `detail` errors.

## Server/client compatibility rules
Version all story editions, API schemas and asset manifests independently. Changing scene graph IDs requires migration; old runs must refer to preserved edition. Mobile must never compute entitlements or blindly trust generated text. Public API OpenAPI contract tests should be added T003-T004.
