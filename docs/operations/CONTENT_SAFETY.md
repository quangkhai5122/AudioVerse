# Content policy and age moderation (initial research spec)

Initial beta audience: adults. Original mystery story avoids explicit sexual content, graphic violence and real-world targets. Future public creator content must not be accepted without moderation, reports and appropriate age classification.

## Moderation lifecycle
Submission/AI draft -> automatic screening for configured content categories -> review queue if uncertain/flagged -> qualified human decision -> age tag and warning -> publish -> ongoing user reports and appeals -> suspend/unpublish if necessary. Model screening has false positives/negatives; never treat an LLM JSON `safe:true` as final publication authorization.

## Controls by surface
- Fixed audio: story synopsis, transcript, actual audio sample and metadata reviewed; source rights verified.
- Interactive generated scene: world allowlist, age policy, model output moderation and prohibited-plot constraints; high-risk output withheld from player.
- Voice input (future): privacy/consent and moderation of user speech; prevent impersonation harassment.
- Public creator/UGC (future): report/block user, moderation history, repeat abuse handling, appeals and platform policy review.

## Staff review record
`{asset_id, edition_id, policy_version, reviewer_id, timestamp, finding, action, appeal_status}` stored in append-only audit. Change policy version requires retroactive risk review for selected content.

## Open questions
What age categories apply under Vietnam game or audiovisual regulations? Which scenes need content warnings? Are users permitted to make public text or only select authored choices? What is procedure for minors? Do not answer by guess; obtain legal and user-research evidence before public release.
