# T001 — Flutter Bootstrap & Device Validation

**Stage:** R1  |  **Status:** DONE (Android-first verified; iOS native requires macOS/Xcode)  |  **Dependencies:** Flutter/Dart + Android SDK/emulator (installed on `D:\`)  |  **As of:** 2026-11-18

## Objective and scope
Generate native Android/iOS wrappers, run `flutter analyze`, implement deterministic widget tests with a fake API/audio controller, build `app-debug.apk`, and verify foreground catalog, MP3 playback, branch traversal, ending reachability, and error recovery on an Android emulator using debug-only cleartext HTTP (`10.0.2.2:8765`).

## Verified Toolchain & Environment Versions (2026-11-18)
- **Flutter:** `3.50.0` (channel `stable`, framework `ab2912035e`, engine `371f77202a`) at `D:\flutter`
- **Dart / DevTools:** Dart `3.14.0`, DevTools `2.61.0`
- **Android SDK (`D:\Android\Sdk`):** Command-line tools / Android CLI `1.1.16919734`, `platform-tools` (`adb` `1.0.41` / `37.0.1-15733141`), `platforms;android-36` & `platforms;android-35`, `build-tools;36.0.0` & `35.0.0`, `ndk;28.2.13676358`, `cmake;3.22.1`, `emulator` `37.2.13.0`
- **Android Virtual Device (`audioverse_api35`):** `system-images;android-35;default;x86_64` (Android 15, API 35, `pixel_6`), hardware acceleration `WHPX (10.0.19045)`
- **Java:** Java `22.0.2+9-70` (`kotlin.incremental=false` set in `mobile/android/gradle.properties` to prevent Kotlin `.tab` incremental cache close error on Windows/JDK 22)

## Acceptance & Evidence Checklist
- [x] Code and native Android/iOS scaffolding (`mobile/android`, `mobile/ios`, `mobile/pubspec.lock`) checked into documented path while preserving `mobile/lib` and `mobile/pubspec.yaml`.
- [x] Relevant requirement ID (`PLY-02`) in `docs/product/requirements.psv` and `docs/product/FUNCTIONAL_SPEC.md` updated from `SOURCE` to `DEMO`.
- [x] Exact tests run and results copied into `docs/agent/SESSION_LOG.md`:
  - `flutter analyze` => `No issues found!`
  - `flutter test -r expanded` => **6 passed** (catalog error & retry, duplicate in-flight submit suppression, branch traversal + memory notes + ending, uncertain transport failure idempotency key retention, committed choice + audio failure recovery, and `409 Conflict` auto-refresh via `getRun`).
  - `flutter build apk --debug` => built `mobile/build/app/outputs/flutter-apk/app-debug.apk`.
  - Android 15 (API 35) Emulator (`emulator-5554`) live E2E against loopback FastAPI (`http://10.0.2.2:8765`): verified offline error state (`Không kết nối được backend local.`), `"Thử lại"` catalog recovery, MP3 streaming (`s0.mp3`, `s1.mp3`, `s3.mp3`, `s4.mp3`, `s8.mp3` HTTP 200), branch traversal `s0 -> s1 -> s3 -> s4 -> s8`, conditional memory note (`◆ An cảm thấy chiếc chìa khóa B trong túi áo.`), ending (`Kết thúc: Hồ sơ còn lại`), and SQLite persistence (`version=4`, 4 events).
- [x] Negative cases, edge conditions and security/rights checks covered:
  - Fixed starter bug where `CatalogScreen` `"Thử lại"` passed a `Future`-returning expression to `setState()`.
  - Fixed `StoryScreen` so committed server state (`_run = run`) is applied before `SceneAudioController.setUrl(...)`, preventing stale client version on audio failure and offering `"Thử tải lại âm thanh"`.
  - Retained pending `(choice_id, expected_version, idempotency_key)` on transport/timeout failures and added `GET /api/v1/runs/{run_id}` auto-refresh on `409 Conflict`.
  - Restricted cleartext HTTP to debug-only (`mobile/android/app/src/debug/res/xml/network_security_config.xml` for `10.0.2.2`, `127.0.0.1`, `localhost`); release manifests remain untouched.
- [x] `PROJECT_STATE.md`, `CURRENT_TASK.md`, `BACKLOG.md`, and `SESSION_LOG.md` updated.
- [x] Clear next task (`T002 — Rights Provenance`) and reproducible first command recorded.

## Deferred to Later Tasks
- **T005:** Background audio (`audio_service`), lockscreen media controls, persistent cross-restart run/position storage, and authorized offline downloads.
- **macOS/Xcode:** Native iOS build and iOS Simulator execution remain unrun on this Windows workstation and must be validated on a macOS environment.
