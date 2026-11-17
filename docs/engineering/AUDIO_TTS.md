# Audio pipeline, TTS, narrator licensing and speech R&D

## Three content paths
1. **Human narrator recording:** only licensed master audio; ingest checks chain of rights for text + performer + sound recording + territorial stream/offline grants; no automatic transformation or voice extraction.
2. **Pre-generated synthetic narration:** text under valid adaptation/TTS grant, approved provider and model license; create once, normalize, QC, store versioned manifest, distribute by authorized edge.
3. **On-demand interactive narration:** only original/derivative-authorized text + voice assets with eligible synthesis rights; generate after deterministic scene validation, cache by content/model/rights/voice version. Avoid private cross-user sharing.

## Pipeline
Licensed input -> quarantine -> rights verifier (qualified human for third-party) -> text preprocessing -> Vietnamese number/acronym/Hán Việt proper-name dictionary -> narrator/speaker mapping -> TTS or authorized recording -> `ffmpeg` normalize to agreed loudness/mono or stereo preset -> verify waveform, duration, silence and checksum -> timestamp transcript -> editorial QA -> approval -> publish private asset -> short-lived streaming authorization.

## Audio technical defaults (starting experiments, not hard constraints)
Speech mono AAC or MP3 48–80 kbps, 24–44.1kHz source as appropriate, normalized integrated loudness with EBU R128 if valid; HLS segmented audio or HTTP Range for robust seeking. Compare device compatibility vs bandwidth. One hour at 64kbps approximately 28.8 MB; 2,000h ~57.6 GB compressed before redundancy.

## Provider abstraction contract
`TTSRequest{text, locale, voice_id, model, speed, emotion, rights_ref, budget_id, idempotency_key}` -> `JobHandle/status` -> `AudioAsset{sha256,duration,codec,characters_billed,model_version,voice_version,rights_ref,cost_estimate,source_trace}`. Log provider request id and billed units; never put API keys on mobile. Bounded timeouts and retries with jitter; duplicate request suppression.

## Provider eval (Vietnamese)
Build 60–100 original/authorized paragraphs stratified by: names from different regions; Sino-Vietnamese terms; dialogue with 2–4 speakers; prose with lists/numbers; loudness/calm, high emotion; long pauses; horror climax; slow descriptive sections. Mean opinion score alone is insufficient. Measure:
- Vietnamese intelligibility (listener error for words/proper names), mean opinion score with blind assessment and confidence intervals.
- Narrator identity stability and prosody across 30-minute chunks; multi-speaker dialogue quality.
- Per-minute generation cost, p50/p95 first-audio delay, failure/retry, allowed speed change.
- Quality of phone listening, Bluetooth, low bitrate, background/interruptions.

## Current provider examples (check latest before implementation)
- FPT AI Factory marketplace TTS Pro roughly $16.50 / 1M characters (confirmed in 2026 research), Ultra higher; old Console plans may no longer apply.
- Google Cloud Chirp HD (~$30/1M characters in earlier check, check official region/model price).
- ElevenLabs v3 (~$100/1M characters in earlier check). Quality/cost must be empirically measured on Vietnamese.
- `espeak -v vi` demo **is not a candidate for paid-product voice quality**. It was used solely to generate original local MP3 fixtures without API billing.

## Self-host/fine-tune decision gate
Only start after 1) commercial use license confirmed for model, pretrained weights and training data; 2) 20h+ representative QA audio licensed for training if the project wants style adaptation (the exact amount depends on model); 3) API baseline's cost/quality/latency limits measured; 4) training/inference GPU cost and test results benchmarked against API; 5) voice owner signs a separate explicit voice synthesis/reuse/territory/term grant. Do not infer voice consent from a podcast recording.

Measure real-time factor `RTF = render_wall_time / generated_audio_duration`. GPU unit cost = GPU $/hour x RTF x audio_hours, plus idle, storage, engineer, failure and preprocessing costs. A model with RTF=0.2 produces one audio hour in ~0.2 GPU-hours *only on the exact benchmarked hardware/setup.*

## Cache policy
Cache keys include `sha256(normalized_script, speaker_spans, voice_version, model_version, synthesis_config, rights_grant_version)`. Shared cache may only contain content permitted for sharing under explicit rights and privacy policy. Consent revoked/contract expires -> prevent new retrieval and purge targeted objects according to legal hold obligations. Download rights separate from stream.

## Future voice interaction
Speech-to-text choice input is separate from narration. Do not retain raw user voice by default; obtain required consent, show transcription for confirmation when ambiguous; don't use recordings for model training unless user explicitly consents and law permits. Voice input from children triggers separate privacy/age review.

## References
https://developers.cloudflare.com/r2/pricing/
https://cloud.google.com/text-to-speech/pricing
https://elevenlabs.io/pricing/api
https://github.com/SWivid/F5-TTS
https://github.com/myshell-ai/MeloTTS
https://github.com/coqui-ai/TTS
