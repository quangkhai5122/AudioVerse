# UX journeys and screen-level behavior

## UX principles
Narration first; controls readable with one hand; story choices are meaningful and accessible; no fake progress/spinners; explicit narrator attribution and synthetic voice badge; costs/entitlements clear; pause/resume is sacred; app works when re-opened after hours or network drop. Vietnamese copy, large tap targets, dynamic font size, TalkBack/VoiceOver, text contrast and caption/transcript alternatives.

## Journey 1: First-time passive listening
1. Open without required login if content free; optional interest selection, skip always.
2. Discover hero stories with verified narration source, length, genre, age category, interactive badge.
3. Tap story: view synopsis, rights-scope features (offline? branching?), number of episodes, narrator disclosure and free preview.
4. Play -> player with sleep timer, speed, chapters, seek, media session -> background continues when screen locks.
5. Save playback position every 15–30s and on pause/end; resume idempotently on same or another device after auth.
6. If network lost, keep current buffered segment, show offline option if authorized, never silently skip chapters.

## Journey 2: Authored branching
1. Listener starts a run at scene S0; app establishes immutable run ID + story version.
2. Narration reaches a choice cue. In active mode pause and show 2–4 choices (with clear, short text), one action per tap. In passive mode follow author-defined default route, if any.
3. Backend validates current version, preconditions, rights, content age gate, entitlement and budget; commits one event exactly once.
4. Client immediately reflects confirmed choice and shows staged progress; if pre-rendered, play instantly; if generated, stream approved intro/fallback while background job completes.
5. Confirm effect via change in next scene/knowledge; allow view 'decision history'. If another device changes run, show conflict/refresh rather than overwrite.
6. At ending show consequences, replay alternate paths, unlock next season if lawful.

## Journey 3: Story with human-narrated fixed content
Human narrator owns/has licensed performance and recording. Display voice credit, rights acknowledgments and source. Serve only the approved audio asset. Never automatically feed transcript/audio into generative branch, training, voice cloning or derivative export if those rights are absent. If author has granted a separate interactive adaptation, manage it as a distinct work/edition and rights chain.

## Journey 4: Creator content onboarding (future)
Invitation -> creator verifies identity and title -> uploads *claimed* rights evidence -> legal reviewer checks grants (work, performance, master, derivative, TTS, training, voice) -> artifact quarantined -> technical QA -> authorized publication window -> stats -> payouts -> expiry/takedown. Creator never self-approves rights; payouts only on reviewed contracts and signed financial ledger.

## Journey 5: Purchase/recovery (future)
Tap locked season -> transparent price, duration, consumption limits and renewal terms -> native store purchase -> server verifies store transaction and ownership -> idempotent entitlement -> listen; restore button uses store transaction reconciliation. No credit issued from a client-only receipt. Failure/timeout: check server status before retry and avoid duplicate charge.

## Journey 6: Audio rendering delayed
UI shows text transcript and verified generation status; no placeholder narration that contradicts canon. User can pause, background, or cancel unbilled future work. Cost spent and job statuses recorded. On provider outage: fallback authored text or pre-generated safe scene, never forced paywall failure without remedy.

## Journey 7: Copyright takedown
Rights expiry, formal complaint or inappropriate content report -> disable new access as required -> freeze new derivatives/TTS -> queue deletion/deindex/offline revalidation -> notify affected users as appropriate -> preserve lawful audit evidence -> reviewer closes the case with traceable outcome.

## Journey 8: Safety / age protection
Age classification before content, warning on potentially distressing material, report button per work, privacy notice for voice input; moderator triages reports. For minors in future, verify applicable age/consent laws and time/spending restrictions before launch.

## Screen inventory
S01 onboarding/safety/consent, S02 discover, S03 search, S04 work detail, S05 fixed player, S06 choice overlay, S07 generating scene/status, S08 scene transcript, S09 decision timeline, S10 library, S11 downloads, S12 paywall, S13 profile/privacy, S14 purchases/restore, S15 reports/support, S16 creator studio work/scene editor, S17 rights reviewer console, S18 operations dashboard, S19 admin audit/takedown, S20 experiment metrics. Current code: browser implements S04/S05/S06/S09 minimally; Flutter library+story/player is source only.

## Copy and interaction contract
Avoid autoplay on page load, never change chosen action without confirmation, allow screen-reader descriptions for choices, no coercive surprise subscriptions, show clearly whether voice is human or AI. Story engine should return structured states to support coherent localization and accessibility.
