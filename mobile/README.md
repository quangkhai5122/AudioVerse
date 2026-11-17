# AudioVerse Flutter UI starter

The `lib/` application is provided; generated native platform templates and lockfile are intentionally **not** included because Flutter SDK is not available in the build environment.

From `mobile/`, with Flutter installed:

```bash
flutter create --platforms=android,ios --project-name audioverse .
flutter pub get
flutter analyze
flutter run --dart-define=API_BASE=http://10.0.2.2:8765
```

- Start backend on `127.0.0.1:8765` beforehand.
- Android emulator: `10.0.2.2` is the development machine. Add INTERNET permission in AndroidManifest.xml. For **local debug only**, configure cleartext HTTP as allowed; production must use HTTPS.
- iOS Simulator uses `http://127.0.0.1:8765`, requiring a *debug-only* App Transport Security exception if HTTP; production HTTPS.
- Physical phones cannot access a server bound only to localhost. Do not expose this demo on LAN/Internet to work around it: authentication and production security are not implemented. Use a secure authenticated preview deployment after T004.
- Basic foreground MP3 playback and branching choice UI are implemented. Background mode, offline download, entitlement, resume and native tests are **planned, not delivered**.
- Flutter SDK not installed in this packaging environment: syntax/integration is provided as a starter, **not Flutter build-verified**. Run `flutter analyze` before implementing additional UI.
