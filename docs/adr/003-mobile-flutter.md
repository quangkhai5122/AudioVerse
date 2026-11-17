# ADR-003: Flutter shared client; start with Android-first testing
**Status:** Accepted for starter **Date:** 2026-11-17

## Decision
Flutter/Dart source for shared Android/iOS. Use just_audio for foreground streaming initially, add audio_service and lifecycle components after native SDK/device tests; basic working browser demo allows integration testing without Flutter toolchain.

## Alternatives
React Native (viable; not selected to avoid mixed stacks); native Kotlin/Swift (higher double maintenance); PWA only (background/offline/store limits).

## Limitations
Flutter SDK absent in initial packaging environment; native directory templates/lockfile not generated. No claim of compile-verified client until T001.
