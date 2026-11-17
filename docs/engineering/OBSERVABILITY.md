# Event analytics, AI cost accounting and experiment metrics

## User event taxonomy (future)
`app_open`, `work_impression`, `work_detail`, `play_started`, `play_buffering`, `play_paused`, `episode_complete`, `choice_offered`, `choice_selected`, `choice_committed`, `choice_conflict`, `generation_requested`, `generation_completed`, `generation_failed`, `tts_started`, `tts_ready`, `download_authorized`, `purchase_offered`, `purchase_verified`, `entitlement_revoked`, `story_reported`.

Common fields: anonymized account/session id (where legally appropriate), app/platform/version, work/edition/scene ids, timestamp UTC, network class (not precise location), experiment id and rights/age-safe metadata. Avoid logging raw story text, payment information or user voice by default.

## Metric definitions
- MAU = distinct eligible active users with meaningful event in trailing 30 days, specify registered vs anonymous.
- D7 retention = distinct users from signup cohort active on day 7 / eligible cohort at day 0; define strict day window.
- Story completion = unique runs reaching end / runs with first scene started, segmented by passive/interactive.
- Choice acceptance = valid submitted choices / intended user choices; exclude retries deduped.
- AI generation spend = sum(provider billable token * price version + TTS chars * price version + GPU seconds + failed retries).
- Contribution margin = recognized net revenue minus store fees, creator royalties, AI costs, storage/delivery variable costs, refunds and variable support.

## Job traces
`request_id`, `run_id`, `scene_id`, `edition_version`, `rights_grant_version`, `provider`, `model`, `prompt_digest`, `input_tokens`, `output_tokens`, `tts_characters`, `cache_hit`, `estimated_usd`, `billed_usd`, `latency_ms`, `retry_count`, `status`. Costs should be reconciled with actual provider invoice daily.

## Alert thresholds proposed
Unexpected >2x hourly cost vs 7-day baseline; sustained generation error >5% for 10m; p95 time-to-audible > agreed beta SLO; unknown rights version on newly served content; failure of billing webhooks or entitlement anomalies; rising playback error count. Tune using observed data, not these initial illustrative values.

## Event privacy and opt-out
Minimize collection, provide legally required transparency/controls, restrict raw event retention and processor access. Avoid using listening interests to infer protected/sensitive attributes; don't personalize sensitive stories without clear user agency.
