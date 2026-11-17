# AudioVerse Product Requirements Document (PRD)

**Document version:** 0.1, 2026-11-17. **Status:** design proposal, not proof of product-market fit.

## 1. The product promise
A Vietnamese listener can discover a compelling audio story, listen without friction, and—where the story rights and authoring permit—take consequential actions that change the journey and ending. Audio should feel as effortless as an audiobook; interaction should feel like a well-written game. **The core value is enjoyment and agency, not the novelty of AI generation.**

## 2. Audience and purchaser
- Primary beta: Vietnamese-speaking adults (18+) who enjoy thriller, mystery, paranormal suspense and serialized audio fiction, with smartphone usage and headphones. The genre is an experiment, not a measured top genre.
- Secondary: readers of long web novels who prefer to listen; consumers of Vietnamese narrators' podcast/YouTube channels under licensed cross-distribution.
- Future creator-side customers: writers/narrators with provable ownership who want distribution, analytics and revenue share; not MVP self-service.
- Payer: individual user through app store subscription/season unlock; creator payouts later.

## 3. Jobs to be done
1. **Casual listening** — "While commuting or before sleeping, I want good Vietnamese narration that resumes where I left off." User outcome: uninterrupted listening of licensed fixed episodes.
2. **Meaningful interaction** — "When I want more agency, let me decide something important and show consequences." Outcome: choice effects visible in scenes and endings.
3. **Content discovery** — "Help me find a story with mood/style/duration I enjoy." Outcome: start new story in fewer taps.
4. **Confidence and ownership** — "Know what my payment unlocks, which audio is AI-narrated, how to restore my purchase, and that my choices won't disappear." Outcome: trustworthy product.
5. **Creators (future)** — "My existing legal recordings can reach listeners and I can track compensation without losing control of rights." Outcome: bounded contract and transparent reporting.

## 4. Problem, wedge and defensibility
Generic audiobook apps excel at passive content. AI storytelling apps excel at unconstrained text prompts but often struggle with coherent arcs, voice quality and predictable cost. AudioVerse combines (a) curated/legally licensed narrations, (b) original authored interactive story graphs, (c) deterministic canonical state, (d) natural Vietnamese TTS and (e) creator network. All components have competitors; differentiation must be validated in playback completion, choice impact, narrative QA, repeat listening, conversion and legal rights acquisition—not asserted.

## 5. Product surfaces
### A. Listener mobile
Discover, serialized catalog, details/metadata, player with chapters, playlist, background/offline, branch prompt, run timeline, library, downloads, purchases, profile/privacy, safety controls.

### B. Content studio (web, authenticated future)
Work/series/episode/scene editor, directed story graph, legal provenance, audio uploads, transcript, versioned publishing, TTS tasks, moderation, preview, schedules, rights expiry, unpublish, takedown.

### C. Internal operations
Support, rights review, billing reconciliation, creator settlement, provider usage/cost, moderation, incidents, analytics, experiment flags, review audit.

## 6. Two mode semantics
**Fixed Audio** may be a human recording or pre-generated TTS; no branching unless licensed for derivatives. Player can stream original by authorized link/asset. **Interactive Audio** comprises narrative world + state + event graph, authored scene audio and AI drafts subject to permitted derivative rights; choices are optional and an authored default path must exist for passive playback. If a user chooses a branch, they cannot be forced to listen to a non-canonical or contradictory scene.

## 7. Core loops
1. **Discover loop:** category/mood -> story sample -> follow -> new episode notification -> completion -> recommendation.
2. **Immersion loop:** play -> optional decision -> meaningful consequence -> world memory -> next scene -> ending -> replay alternative.
3. **Creator loop (later):** approve rights -> ingest recording/original -> QA -> publish -> listeners -> analytics -> royalty settlement -> more stories.
4. **Monetization loop:** free preview -> show price before generation/unlock -> server verified entitlement -> consume within bounded quota -> restore purchases.

## 8. North-star and guardrails
North-star candidate: **qualified weekly listening sessions** (a session with >=10 minutes of verified playback or a completed meaningful interactive chapter); not raw generated token count or app installs.

Product metrics: D1/D7/D30 retention by cohort; listening hours per WAU; episode completion; next-episode continuation; interactive opt-in; choice-impact survey; paywall conversion; paid churn; creator acquisition and license renewal. AI quality: contradictions per 100 transitions, consistency, p50/p95 branch time to audible sound, TTS pronunciation error per minute, abandon-during-generation. Economics: contribution margin per paying user including inference, licensed royalty and store fees. Safety: copyright/rights incidents, blocked unlicensed derivatives, moderation false-negatives, playback crash-free sessions and data loss events.

## 9. Release scope
- **Demo (current):** one original 11-scene branching story, synthetic MP3, browser player, API, Flutter source. No paid/public deployment.
- **Alpha:** tested Flutter foreground/background player; curated 2–3 originals; fully versioned graph; real auth + content manifests; bounded AI beta behind sign-off; no production payments unless applicable compliance ready.
- **Commercial beta (after gates):** licensed content from a small number of creators, auditable moderation, secure media access, IAP, rights takedown, privacy/export, store review, Vietnamese legal classification approval.
- **Expansion:** multi-voice expressive narration, open-text choices, offline secure download, creator studio, recommendations, voice R&D.

## 10. Not in scope for MVP
Illegal scraping/rehosting YouTube, arbitrary URL-to-audio rehost, voice cloning without rights, arbitrary fan-fiction of copyrighted universes, public creator uploads without moderation, unbounded free-generation, AI self-modifying canon, person-to-person chat, automatic publishing of medical/legal/unsafe content, live voice conversation, all-language localization.

## 11. Product-market fit experiments
- R1: 20–30 users qualitatively listen to a single original story; measure audiobook usability and whether 3 choices feel consequential.
- R2: A/B an identical fixed story vs its interactive adaptation; measure completion, interruption frustration and desire to play another chapter.
- R3: ~100–300 beta participants from ethically recruited reader communities; measure 7-day return, p95 latency, per-user inference, demand for next series; then ask for a real paid unlock after legal/store gates.
- Kill/pivot criteria (suggested, not law): most users prefer fixed only; majority of interactive scenes fail continuity checks; cost exceeds willingness-to-pay without acceptable caching; legally authorized source catalog unavailable; or game licensing not viable.

## 12. Major dependencies
Vietnam game/service counsel, chain of title for each work + derivative/voice permission, mobile account and app store billing policies, an authorized content pipeline, quality-assured Vietnamese TTS, security and production SRE.

## 13. Explicit unresolved questions
Which genres actually retain Vietnamese users? Will narrators license existing recordings? Do listeners prefer tap choices vs voice input? How much latency will users tolerate? Can the story writer preserve meaningful divergence after 20+ actions? What store/legal category applies? How much will creators demand in royalties? Run experiments before treating any answers as facts.
