# AudioVerse — inspectable unit economics and hosting cost model

**As of 2026-11-17.** This is a scenario model, **not a vendor quotation or forecast**. Verify each provider price before buying. Use `python scripts/cost_model.py` for calculated scenarios, not hardcoded numbers from this document.

## Fixed model assumptions
- Narration text density: **45,000 Unicode characters per finished audio hour**. Recompute from a representative Vietnamese corpus and provider billing semantics; very sensitive to reading speed and whitespace counting.
- 64 kbps mono audio: **28.8 MB per hour**, before CDN segments, redundancy, multi-bitrate and backups.
- Reference API rates: FPT TTS Pro **$16.50/1M chars**; Google Chirp HD roughly **$30/1M**; ElevenLabs v3 about **$100/1M**. Rates may vary by endpoint, region and contract. FPT's earlier personal Console plans were discontinued/restructured by 2026; do not use stale personal price.
- Example narrative LLM scene = 4,000 input tokens, 700 output tokens, 2 minutes of produced content; 30 scenes/hour. Low-cost provider example `$0.14/1M input, $0.28/1M output` gives `$0.02268/hour`. Higher tier example `$1.40/$4.40` gives `$0.2604/hour`. These are *cost examples* not model quality predictions.
- Cloudflare R2 Standard storage $0.015/GB-month with 10 GB-month free, Class A $4.50/M ops and Class B $0.36/M ops after free allowances. Egress is listed as free for standard service; edge compute, caching, API and other services may cost extra.
- Revenue conversion scenario: VIP at 59,000 VND/month; exchange **26,000 VND/USD planning assumption**, app store fee **15% assumed eligibility**; content royalty **30% of amount after store fee**, and net of refunds/taxes needs refinement.

## Main formulas
`generated_hours = MAU × personalized_minutes_per_active_user ÷ 60`.
`tts_cost = (new_fixed_hours + generated_hours) × characters_per_hour ÷ 1e6 × tts_rate_per_million`.
`llm_cost = generated_hours × scenes_per_hour × (input_tokens_per_scene × input_rate + output_tokens_per_scene × output_rate) ÷ 1e6`.
`storage_GB = stored_audio_hours × bitrate_kbps × 3600 ÷ 8 ÷ 1e6`.
`gross_usd = MAU × paid_share × price_vnd ÷ fx_vnd_usd`.
`post_store_royalty_usd = gross × (1 - store_fee) × (1 - royalty_of_post_store)`.
`contribution = post_store_royalty - audio_tts_cost - narrative_llm - monthly_infra - marketing - other_variable_costs`.

Cost-accounting caveat: Some story audio is fully reused (pre-rendered), so generated_hours should reflect **actual new renders**, not all playback hours. Caches must obey privacy/rights. Include provider retries, re-render QA, failed generations and free-user spending, not only paying users.

## Storage sensitivity
| Library duration | Size at 64 kbps | R2 monthly storage only (excluding rounded billing/free and operations) |
|---|---:|---:|
| 100 h | 2.88 GB | $0.0432 nominal |
| 1,000 h | 28.8 GB | $0.432 nominal |
| 10,000 h | 288 GB | $4.32 nominal |

Cloudflare rounds up billing units; after the Standard free allowance, actual bills differ. Storage is not the main cost driver; paid narrators, rights, content editing, acquisition and on-demand TTS/LLM usually matter more.

## Three illustrative operational scenarios
Alpha 300 MAU with 30 new fixed hours and 20 dynamic hours/month; small launch 3,000 MAU with 100 fixed and 300 dynamic hours; growth 30,000 MAU with 300 fixed and 3,000 dynamic hours. `scripts/cost_model.py` calculates exact AI/infra estimates under an assumption set. These are arbitrary volumes for capacity planning; not forecasts or target KPIs.

## Threshold and risk
With 59k VND VIP, 15% store fee and 30% royalty post-store, residual per paying user = `59000 * .85 * .70 = 35,105 VND` before TTS, LLM, infra, acquisition, refunds, taxes and content production. Thus personal AI audio for 1–3 hours/month can consume a large fraction of marginal contribution. Free users consuming on-demand AI can drive losses even before anyone pays.

## Revenue models to test
Fixed library subscription; paid interactive minutes/scene packs; seasonal unlocks; creator-specific subscriptions; selectively ad-supported free episode trials. Keep server verified entitlements, visible quotas and refunds. If coin gaming mechanics apply, consult Vietnam online-game rules first.

## Biggest unknowns
Real user MAU and retention, paid conversion, CAC, content licensor royalty/minimum guarantee, willingness to pay, actual interactive minutes per user, TTS character density and quality, LLM retry+failure rate, content review burden, license/regulatory costs and mobile app store approval.

## Official reference links (verify again at implementation)
- https://developers.cloudflare.com/r2/pricing/
- https://cloud.google.com/text-to-speech/pricing
- https://elevenlabs.io/pricing/api
- https://supabase.com/pricing
- https://railway.com/pricing
- https://www.revenuecat.com/pricing/
- https://developer.apple.com/app-store/small-business-program/

## Practical financial go/no-go
Never set unlimited AI plan pricing before beta cost ledger. Decide `max generated chars and tokens` per plan from measured cost at p95 usage and target contribution margin. Post-transaction receipts verified server-side; maker/checker royalty approvals separate from content editorial approval.
