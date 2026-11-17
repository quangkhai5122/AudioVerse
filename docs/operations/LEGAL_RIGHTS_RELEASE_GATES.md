# Content rights, Vietnam classification and legal release gates

**Engineering policy, not legal advice.** As of 2026-11-17. Qualified Vietnamese counsel/rights specialist must assess actual app features, story ownership, player use, payment and audience before any production launch.

## L0 — classify product BEFORE commercial rollout
AudioVerse is partly an audiobook distributor and partly an interactive service/game where users interact with server-generated story state. Under Decree 147/2024/ND-CP and amendments including Decree 116/2026/ND-CP, online electronic game classifications G1–G4 (particularly G2 for player-server interaction) may be relevant. **Do not assert** the app is definitely G2 or definitely outside game regulation merely because it uses words 'story' or 'book'. Review business entity, permit/certificate, content approval, hosting, player age, data retention, payments, local infrastructure and app category with competent counsel and applicable authority.

Official starting point: https://game.gov.vn/ and published game-regulation guides; consolidated regulatory texts and competent regulator publications take precedence over SEO summaries. Write a dated lawyer's opinion and resulting requirements before public distribution.

## L1 — legal chain of title
For each work/edition/asset, separately identify:
1. Underlying literary work author(s), current economic rights holder, original language.
2. Translated/edited screenplay rights holder where applicable.
3. Performer's neighboring rights for narration; employer/producer contracts and transfers.
4. Sound-recording/master rights holder and rights to distribute the specific files.
5. Derivative/interactive adaptation rights distinct from stream or download rights.
6. Permission to synthesize speech from story text distinct from audio-recording reproduction.
7. Explicit separate permission to clone/fine-tune/recreate a recognizable person's voice, including output exploitation terms, revocation, use after expiry.
8. AI model weights/data/commercial inference licenses and provider retention/secondary-training terms.
9. Music/sound effect rights and territorial/term/offline restrictions.
10. Attribution and creator royalty duties.

**Unverified audio is quarantined.** Creator upload, a YouTube URL, or an RSS feed do NOT count as proof of license. Do not import/scrape/rehost without required grants. Embedding an official player is not equivalent to owning stream assets; comply with provider terms and player restrictions.

## L2 — permission matrix and automated gates

| Action | Required grant | Can stream-only grant permit? |
|---|---|---|
| Stream owned recording | Work + performance/master stream in relevant scope | Yes only if all relevant rights held |
| Download/cache offline | Explicit download/offline terms | Not by default |
| Alter transcript/create branches | Derivative/adaptation of work and possibly adaptation of recording | No |
| AI TTS of copyrighted story | Appropriate rights to transform/use text and create/distribute output | No |
| Clone human narrator voice | Separate voice/performer/recording consent and approved terms | No |
| Train model on text/audio | Explicit training/data rights and lawful processing | No |
| Generate new stories in established universe | Derivative authorization where protected work/characters implicated | No |
| Publicly share user-generated derivative | Publishing plus UGC/content moderation rights and controls | No |

## L3 — review workflow and data model
`DRAFT -> EVIDENCE_SUBMITTED -> UNDER_REVIEW -> APPROVED(with scope/version) -> PUBLISHED -> EXPIRING -> EXPIRED/REVOKED/TAKEDOWN`.
Qualified human reviewer (distinct from submitting creator) approves signed evidence and approved rights in a database with append-only audit. Production rights checks derive permissions from **approved contract versions**, effective term/territory/edition, not a creator-editable boolean. Every TTS/LLM job, stream URL and download revalidates right at action time.

## L4 — app-store and financial rules
Review Apple App Review Guidelines (copyright/UGC/IAP), Google Play intellectual property/payments/user data and developer policies, in-app digital goods/season unlock/coin design and subscription cancellation/restore rules. Child access, content age, generated adult/violent material and user reports may alter eligibility and moderation obligations.

- https://developer.apple.com/app-store/review/guidelines/
- https://support.google.com/googleplay/android-developer/answer/9888072
- https://developers.google.com/youtube/v3/terms/developer-policies
- https://vanban.chinhphu.vn/ (primary texts and updates)

## L5 — privacy and content rules
Consider Vietnam Law on Personal Data Protection 91/2025/QH15 and implementing rules; review age, profiling, ASR recording, voice biometrics, cross-border transfers, processors, deletion, user transparency. Avoid real voice input in alpha and do not train on personal conversation by default. AI-generated public stories require content/safety filters and human escalation.

## Release blocker checklist
- [ ] Written expert determination of applicable service/game licensing and any required permits.
- [ ] Rights registry with signed per-asset chain of title, country and term.
- [ ] Derivative and voice rights auditable for interactive scenes; signed performer consent if cloning.
- [ ] Published terms/privacy, purchase disclosure and content safety rules reviewed.
- [ ] Legal approval of payment and marketing claims.
- [ ] Store compliance review with evidence.
- [ ] Takedown/appeals path tested, including already cached/downloaded media where feasible.
- [ ] Periodic rights expiry tests and admin separation of duties.

No agent may mark a checkbox on behalf of counsel or owner without documentary evidence.
