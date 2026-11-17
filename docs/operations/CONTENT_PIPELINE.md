# Content ingestion, curation and publishing runbook

## Objective
Combine (a) existing authorized narrated recordings, (b) new human performances, (c) authorized AI TTS and (d) original interactive branches without importing unauthorized media. All outside uploads enter quarantine; no automated license approval.

## Process
**Intake:** creator contact, business identity, work identifier, author credits, proposed mode, territory and period. Creator supplies evidence, contracts and raw assets through authenticated HTTPS once T008 exists. Demo has no upload API.

**Rights review:** resolve text copyright, translation, performer rights, recording master, music/SFX, permitted stream/offline/derivative/TTS/voice clone/train actions and royalties. Store reviewer identity and evidence digest. If ambiguous: reject or ask clarification, never infer approval from public posting.

**Technical ingest:** quarantine bucket; malware/type/size checks; SHA-256 dedup within permitted rights scope; metadata extraction (codec, sample rate, channels, loudness, duration); validate transcript alignment, title, chapter boundaries and creator attribution; scan silence, clipping, repeated sections.

**Editorial:** human reviews narration quality, language, storyline, metadata, sensitive content age rating; no generative adaptation without relevant grant. Perform native-speaker listen test on a representative sample, full listen for high-risk scenes.

**Publish:** assign immutable edition, per-scene asset IDs and rights version; prepare CDN object and index; publish at scheduled UTC time with localized display; smoke-test playback and takedown. Do not reference raw public URLs as production assets.

**Renewal:** automated warnings 60/30/7 days before rights expiry, with configurable grace handling per legal agreement; pause new downloads/derivatives before expiry where required. Store cancellation and audit logs.

**Rights dispute:** immediate safe suspension while reviewed; creator dispute process; preserve needed evidence; propagate delete/unpublish to origin/CDN/downstream cache and entitlements as law/contract requires. Never silently delete audit logs under active lawful hold.

## Metadata manifest (proposed)
```json
{
  "asset_id": "audio-uuid", "work_id": "work-id", "edition_id": "edition-hash",
  "source_type": "human_narration", "original_url": "creator-supplied reference only",
  "sha256": "...", "transcript_ref": "...", "length_seconds": 600,
  "voice_owner_id": "...", "master_owner_id": "...",
  "rights_grant_id": "approved-version-id", "rights": ["stream"],
  "territories": ["VN"], "start_at": "YYYY-MM-DD", "end_at": "YYYY-MM-DD",
  "reviewer_id": "...", "reviewed_at": "...", "status": "quarantine"
}
```

All demo asset provenance lives in `content/licenses/demo_license.json`; it is not a production manifest and cannot authorize a third-party audio upload.
