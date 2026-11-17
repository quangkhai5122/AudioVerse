# AudioVerse Flutter Mobile Client

The `mobile/` package contains the Flutter client for AudioVerse, with generated `android/` and `ios/` platform wrappers and deterministic widget tests.

## Toolchain & Verification (Windows)

```powershell
cd mobile
flutter doctor -v
flutter pub get
flutter analyze
flutter test -r expanded
flutter build apk --debug
```

## Running with the Local Demo Backend

1. Start the FastAPI backend on loopback (`127.0.0.1:8765`) from the repository root:
   ```powershell
   .\.venv\Scripts\python.exe -m audioverse.main
   ```
2. Launch on Android Emulator:
   ```powershell
   cd mobile
   flutter run --dart-define=API_BASE=http://10.0.2.2:8765
   ```

## Security & Network Boundaries

- **Debug-only Cleartext HTTP:** `android/app/src/debug/AndroidManifest.xml` and `android/app/src/debug/res/xml/network_security_config.xml` permit cleartext HTTP **only** in debug builds and **only** to `10.0.2.2`, `127.0.0.1`, and `localhost` (`base-config cleartextTrafficPermitted="false"`).
- **Release Manifest Preserved:** `android/app/src/main/AndroidManifest.xml` and `ios/Runner/Info.plist` do **not** enable arbitrary cleartext HTTP.
- **No LAN Exposure:** Do not bind the local demo backend to `0.0.0.0` or LAN for physical phone testing; `X-Demo-Actor` is not real authentication.

## Implemented Foreground Guarantees (T001)

- **Deterministic State Before Audio Load:** `StoryScreen` commits the server-returned `StoryRun` to UI state before calling `SceneAudioController.setUrl(...)`. If audio loading fails after a choice is committed on the server, the UI stays on the new scene/version and offers `"Thử tải lại âm thanh"` instead of leaving a stale version.
- **Pending Idempotency Key Retention:** Transport/timeout errors on choice submission retain the pending `(choice_id, expected_version, idempotency_key)` tuple so retrying the same choice reuses the original key.
- **Automatic 409 Refresh:** If the server returns HTTP `409 Conflict` on a choice, `StoryScreen` fetches `GET /api/v1/runs/{run_id}` (`AudioVerseApi.getRun`) to synchronize with the latest canonical server state.
- **Deferred to T005:** Background playback (`audio_service`), lockscreen controls, persistent cross-restart run/position storage, and authorized offline downloads remain scoped to `T005`.
