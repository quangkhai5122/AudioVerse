# Media storage and streaming design

## Local demo
11 synthetic MP3 fixtures served directly from `media/demo/` at `/api/v1/audio/{scene_id}.mp3`. No user authentication or DRM. **Do not expose** these endpoints publicly to model production architecture.

## Production goals
Private object storage; media delivery only after user auth, content publication, age/territory/time rights checks, subscription entitlements and per-asset offline grant. Serve short-lived signed playback authorization through an edge/gateway that enforces scope. Avoid issuing full-bucket public links. Support byte-range/HLS seek with signed playlists or authorized segment access.

## Protocol decision
MP3 HTTP Range initially for speech simplicity; test HLS for efficient multi-segment download, expired tokens, CDN cache behavior and mobile support; do not force DASH if iOS playback support is limited. Example output formats AAC/MP3 48–80 kbps speech, loudness normalization QA. Audio bitrate alone does not define intelligibility; benchmark devices and the voice.

## Performance and accounting
One hour at 64kbps = 28.8 MB. 10,000 users x 20h/month = 5.76 TB audio served at that bitrate, excluding retry, HTTP overhead and multiple bitrates. Cloudflare R2 Standard currently lists zero Internet egress fee, but request costs, edge processing, caching and operational constraints still apply. If moving to another provider, egress economics can dominate.

## Security/failure cases
Revoked license, expired subscription, signed URL replay, path traversal, SSRF from arbitrary source URLs, malicious uploaded media, CDN cache purging, poor connectivity, partial MP3 download, background access, offline copy after permitted term. No unrestricted download endpoint for license-limited recordings.

## T004 threat tests
Authentication/authorization before media issuance; no cross-user protected asset access; download entitlement distinct from stream; URL TTL; rights version mismatch fails closed; audio request logged without sensitive story text; CDN caching configured per asset/publicity.
