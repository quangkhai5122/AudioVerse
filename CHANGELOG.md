# Changelog

## T001 Flutter bootstrap & Android emulator validation — 2026-11-18
- Installed Flutter 3.50.0 (Dart 3.14.0) and Android SDK/NDK/CMake/Emulator on workstation; generated native `mobile/android` and `mobile/ios` project scaffolding and `pubspec.lock`.
- Configured debug-only loopback cleartext HTTP (`10.0.2.2`, `127.0.0.1`, `localhost`) via Android debug `network_security_config.xml` without weakening release manifests.
- Added `SceneAudioController` abstraction, `ApiException`, and `AudioVerseApi.getRun`; fixed `CatalogScreen` `setState` returning `Future` bug; updated `StoryScreen` to commit server run state before audio load, retain pending idempotency key on transport errors, and auto-refresh on HTTP 409.
- Verified `flutter analyze` (0 issues), 6 deterministic widget tests, `flutter build apk --debug`, and live headless Android 15 (API 35) emulator end-to-end flow (`s0 -> s1 -> s3 -> s4 -> s8`) against local FastAPI backend.

## T000 onboarding audit — 2026-11-17
- Verified Windows/Python backend, repository, lint and loopback HTTP/media baseline; retained unrun Flutter/browser/device checks explicitly.
- Persisted owner-authorized long-term commit/push and handoff protocol; audited roadmap and T001 toolchain prerequisites.
- Corrected eight existing one-line-statement lint issues and seven import-order issues; ignored generated egg-info. No product/API/story/rights change.

## 0.1.0 — 2026-11-17
- Original 11-scene mystery with three authored endings and local synthetic narration.
- FastAPI catalog/run/choice/scene streaming and browser UI.
- Deterministic canonical state engine, SQLite run/event storage and idempotent API.
- Flutter Android/iOS client source starter (native wrappers/toolchain verification pending).
- Long-term agent operating manual, 182 functional requirements, 16 task packets, eight ADRs.
- Legal/rights/voice/AI and commercial-release gates intentionally NOT passed.
