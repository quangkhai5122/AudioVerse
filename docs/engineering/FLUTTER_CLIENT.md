# Flutter native application architecture

## Current state
`mobile/lib/` includes working-design Dart source for catalog, original story run, deterministic choice navigation and foreground audio via just_audio. The SDK is unavailable in build container, so **native compilation has not been checked**. Run T001 first; no production app release before mobile test evidence.

## Recommended target architecture
`core/network` authenticated API client and retries, `core/storage` encrypted/session-aware local cache, `features/catalog`, `features/player`, `features/story`, `features/purchases`, `features/account`, `features/downloads`. Riverpod/provider + go_router could be adopted via ADR once UI grows; don't add heavy dependencies without need.

## Audio playback requirements
Single audio handler/service shared across screens; playlists and per-episode progress; headset/bluetooth; phone interruptions; playback notification; delayed authorization renewal; exponential reconnect; 48/64kbps speech presets. Android foreground service permission/config only when required. iOS audio background mode only when truly implemented. Use HTTPS in production; debug localhost cleartext exceptions must not enter release manifests.

## Local persistence
Guest store run ID+scene, progress and playback status in SQLite/Drift or secure store as appropriate; identity and paid entitlement never depend solely on local data. Sync after account login with server version checks. Keep offline caches scoped to rights expiration; do not treat saving a URL as a durable license.

## Platform matrix
- Android emulator API 26+ / modern target SDK set by current Flutter; Android 10–16 device sanity, reduced-power handset.
- iOS Simulator latest supported plus one older supported version; sleep timer, audio interruptions, background behavior, app lifecycle.
- Test Android 4G loss during generation and HLS/MP3 seek; iOS memory pressure and process kill; correct behavior when Bluetooth disconnects.
- Accessibility: screen reader, large font, high contrast, subtitles, choices not entirely audio-dependent.

## UI design system seed
Palette deep midnight navy `#0D1220`, dark panel `#151E31`, teal `#67D8C4`, warm gold `#E5BC7B`; cards for story, branches and progress. Good text hierarchy and touch targets >44pt. Fewer distractions in passive listening mode. No fake CTA, no misleading paywalls.

## Production player state machine
`idle -> authorizing -> loading -> ready -> playing <-> paused -> buffering -> completed`; network/provider errors into `recoverable_error` or `fatal_error`. For interactive stories, `choice_pending -> choice_committed -> audio_rendering -> audio_ready`; never replay an uncommitted choice.

## T001 validation requirements
`flutter doctor -v`, `flutter pub get`, `flutter analyze`, `flutter test`, Android emulator smoke, iOS simulator smoke if macOS available, backend Python tests. The included `mobile/test` widget smoke is intentionally small and must be extended to cover mocked API and state transition.
