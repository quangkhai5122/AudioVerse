import 'dart:async';
// ignore: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:audioverse/main.dart';
import 'package:audioverse/models/story_models.dart';
import 'package:audioverse/screens/story_screen.dart';
import 'package:audioverse/services/api_client.dart';
import 'package:audioverse/services/scene_audio_controller.dart';

class FakeSceneAudioController implements SceneAudioController {
  final StreamController<bool> _playing = StreamController<bool>.broadcast();
  final StreamController<Duration> _position =
      StreamController<Duration>.broadcast();

  final List<String> loadedUrls = <String>[];
  final Set<String> failUrlsOnce = <String>{};
  bool isPlaying = false;
  bool pausedByInterruption = false;
  bool disposed = false;
  Duration currentPosition = Duration.zero;
  double currentSpeed = 1.0;

  @override
  Stream<bool> get playingStream => _playing.stream;

  @override
  Stream<Duration> get positionStream => _position.stream;

  @override
  Duration? get duration => const Duration(seconds: 30);

  @override
  Duration get position => currentPosition;

  @override
  double get speed => currentSpeed;

  @override
  Future<void> stop() async {
    isPlaying = false;
    pausedByInterruption = false;
    _playing.add(false);
  }

  @override
  Future<void> setUrl(String url) async {
    if (failUrlsOnce.remove(url)) {
      throw Exception('Audio codec/stream error for $url');
    }
    loadedUrls.add(url);
  }

  @override
  Future<void> play() async {
    isPlaying = true;
    pausedByInterruption = false;
    _playing.add(true);
  }

  @override
  Future<void> pause() async {
    isPlaying = false;
    pausedByInterruption = false;
    _playing.add(false);
  }

  @override
  Future<void> seek(Duration target) async {
    final maxDur = duration ?? Duration.zero;
    var clamped = target < Duration.zero ? Duration.zero : target;
    if (maxDur > Duration.zero && clamped > maxDur) {
      clamped = maxDur;
    }
    currentPosition = clamped;
    _position.add(clamped);
  }

  @override
  Future<void> seekRelative(Duration offset) async {
    await seek(currentPosition + offset);
  }

  @override
  Future<void> setSpeed(double newSpeed) async {
    currentSpeed = newSpeed.clamp(0.8, 2.0).toDouble();
  }

  @override
  Future<void> handleInterruption({
    required bool begin,
    bool shouldResume = true,
  }) async {
    if (begin) {
      if (isPlaying) {
        isPlaying = false;
        pausedByInterruption = true;
        _playing.add(false);
      }
      return;
    }
    if (pausedByInterruption && shouldResume) {
      pausedByInterruption = false;
      isPlaying = true;
      _playing.add(true);
    } else {
      pausedByInterruption = false;
    }
  }

  @override
  void dispose() {
    disposed = true;
    _playing.close();
    _position.close();
  }
}

class FakeAudioVerseApi extends AudioVerseApi {
  FakeAudioVerseApi();

  bool failCatalogOnce = false;
  bool failNextChoiceWithTransportError = false;
  bool failNextChoiceWith409 = false;
  bool offlineLeaseValidOnServer = true;
  DateTime offlineLeaseExpiresAt = DateTime.now().toUtc().add(
    const Duration(hours: 24),
  );
  Completer<StoryRun>? delayedChoiceCompleter;

  final List<String> submittedIdempotencyKeys = <String>[];
  final List<int> submittedExpectedVersions = <int>[];
  final List<int> savedPositionsMs = <int>[];
  final List<double> savedSpeeds = <double>[];
  int getRunCalls = 0;

  static const StorySummary demoStory = StorySummary(
    id: 'ben-kia-canh-cua',
    title: 'Bên Kia Cánh Cửa',
    description:
        'Truyện kỳ bí tương tác nguyên bản dùng để kiểm thử AudioVerse.',
    genre: 'Kỳ bí / Trinh thám',
  );

  static const Map<String, SceneInfo> scenes = <String, SceneInfo>{
    's0': SceneInfo(
      id: 's0',
      title: 'Tín hiệu lúc nửa đêm',
      text: 'Mưa rơi trên mái tôn trạm phát thanh bỏ hoang.',
      choices: <StoryChoice>[
        StoryChoice(id: 'follow-tracks', label: 'Lần theo dấu chân về kho'),
        StoryChoice(id: 'climb-stairs', label: 'Đi lên tầng hai ngay'),
      ],
      memoryNotes: <String>[],
      ending: false,
    ),
    's1': SceneInfo(
      id: 's1',
      title: 'Trong kho thiết bị',
      text: 'Một chiếc máy ghi âm nằm dưới chiếc bàn phủ bụi.',
      choices: <StoryChoice>[
        StoryChoice(id: 'take-key', label: 'Giữ chìa khóa B'),
      ],
      memoryNotes: <String>[],
      ending: false,
    ),
    's3': SceneInfo(
      id: 's3',
      title: 'Cánh cửa phía dưới',
      text: 'Một hành lang hẹp dẫn đến phòng lưu trữ dưới tầng hầm.',
      choices: <StoryChoice>[
        StoryChoice(
          id: 'open-cellar',
          label: 'Mở cửa tầng hầm bằng chìa khóa B',
        ),
      ],
      memoryNotes: <String>['An cảm thấy chiếc chìa khóa B trong túi áo.'],
      ending: false,
    ),
    's8': SceneInfo(
      id: 's8',
      title: 'Kết thúc: Hồ sơ còn lại',
      text: 'Khi trời hửng sáng, An mang những tài liệu tìm được ra khỏi trạm.',
      choices: <StoryChoice>[],
      memoryNotes: <String>[],
      ending: true,
    ),
  };

  StoryRun serverRun = StoryRun(
    id: 'run-demo-1',
    storyId: demoStory.id,
    version: 0,
    scene: scenes['s0']!,
  );

  List<StoryRun> continueListeningRuns = <StoryRun>[];

  @override
  Future<List<StorySummary>> catalog() async {
    if (failCatalogOnce) {
      failCatalogOnce = false;
      throw Exception('Connection refused');
    }
    return <StorySummary>[demoStory];
  }

  @override
  Future<StoryRun> begin(String storyId) async {
    serverRun = StoryRun(
      id: 'run-demo-1',
      storyId: storyId,
      version: 0,
      scene: scenes['s0']!,
    );
    return serverRun;
  }

  @override
  Future<StoryRun> getRun(String runId) async {
    getRunCalls += 1;
    return serverRun;
  }

  @override
  Future<List<StoryRun>> continueListening() async => continueListeningRuns;

  @override
  Future<StoryRun> saveProgress(
    StoryRun run, {
    required int positionMs,
    required double playbackSpeed,
  }) async {
    savedPositionsMs.add(positionMs);
    savedSpeeds.add(playbackSpeed);
    serverRun = StoryRun(
      id: run.id,
      storyId: run.storyId,
      editionId: run.editionId,
      version: run.version,
      positionMs: positionMs,
      playbackSpeed: playbackSpeed,
      scene: run.scene,
    );
    return serverRun;
  }

  @override
  Future<OfflineSceneLease> createOfflineLease(
    String workId,
    String sceneId,
  ) async => OfflineSceneLease(
    leaseId: 'lease-$sceneId',
    sceneId: sceneId,
    editionId: 'ben-kia-canh-cua-ed1',
    downloadUrl: '/api/v1/media/demo-audio-$sceneId?token=signed-offline',
    sha256: 'a' * 64,
    byteSize: 100000,
    transcript: scenes[sceneId]?.text ?? '',
    expiresAt: offlineLeaseExpiresAt,
  );

  @override
  Future<bool> validateOfflineLease(String leaseId) async =>
      offlineLeaseValidOnServer;

  @override
  Future<StoryRun> choose(
    StoryRun run,
    String choiceId,
    String idempotencyKey,
  ) async {
    submittedIdempotencyKeys.add(idempotencyKey);
    submittedExpectedVersions.add(run.version);

    if (delayedChoiceCompleter != null) {
      return delayedChoiceCompleter!.future;
    }

    if (failNextChoiceWithTransportError) {
      failNextChoiceWithTransportError = false;
      throw Exception('SocketException: Network unreachable');
    }

    if (failNextChoiceWith409) {
      failNextChoiceWith409 = false;
      serverRun = StoryRun(
        id: run.id,
        storyId: run.storyId,
        version: run.version + 1,
        scene: scenes['s3']!,
      );
      throw const ApiException(
        409,
        '{"detail":"Run was changed; reload the latest state"}',
      );
    }

    if (run.version != serverRun.version) {
      throw const ApiException(
        409,
        '{"detail":"Run was changed; reload the latest state"}',
      );
    }

    final String nextSceneId = switch (choiceId) {
      'follow-tracks' => 's1',
      'take-key' => 's3',
      'open-cellar' => 's8',
      _ => 's8',
    };

    serverRun = StoryRun(
      id: run.id,
      storyId: run.storyId,
      version: run.version + 1,
      playbackSpeed: serverRun.playbackSpeed,
      scene: scenes[nextSceneId]!,
    );
    return serverRun;
  }
}

void main() {
  testWidgets(
    'Catalog displays headline, recovers from error, and navigates to story',
    (WidgetTester tester) async {
      final api = FakeAudioVerseApi()..failCatalogOnce = true;
      final audio = FakeSceneAudioController();

      await tester.pumpWidget(
        AudioVerseApp(api: api, audioControllerBuilder: () => audio),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('Một câu chuyện'), findsOneWidget);
      expect(find.text('Không kết nối được backend local.'), findsOneWidget);

      await tester.tap(find.text('Thử lại'));
      await tester.pumpAndSettle();

      expect(find.text('Bên Kia Cánh Cửa'), findsOneWidget);
      expect(find.text('Bắt đầu trải nghiệm'), findsOneWidget);

      await tester.tap(find.text('Bắt đầu trải nghiệm'));
      await tester.pumpAndSettle();

      expect(find.text('Tín hiệu lúc nửa đêm'), findsOneWidget);
    },
  );

  testWidgets(
    'In-flight choice disables duplicate submit until completion',
    (WidgetTester tester) async {
      final completer = Completer<StoryRun>();
      final api = FakeAudioVerseApi()..delayedChoiceCompleter = completer;
      final audio = FakeSceneAudioController();

      await tester.pumpWidget(
        MaterialApp(
          home: StoryScreen(
            story: FakeAudioVerseApi.demoStory,
            api: api,
            audioController: audio,
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.ensureVisible(find.text('Lần theo dấu chân về kho'));
      await tester.tap(find.text('Lần theo dấu chân về kho'));
      await tester.pump();

      await tester.tap(
        find.text('Lần theo dấu chân về kho'),
        warnIfMissed: false,
      );
      await tester.pump();
      expect(api.submittedIdempotencyKeys.length, equals(1));

      completer.complete(
        StoryRun(
          id: 'run-demo-1',
          storyId: FakeAudioVerseApi.demoStory.id,
          version: 1,
          scene: FakeAudioVerseApi.scenes['s1']!,
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Trong kho thiết bị'), findsOneWidget);
    },
  );

  testWidgets(
    'Story flow traverses branch, renders memory notes, and reaches ending',
    (WidgetTester tester) async {
      final api = FakeAudioVerseApi();
      final audio = FakeSceneAudioController();

      await tester.pumpWidget(
        MaterialApp(
          home: StoryScreen(
            story: FakeAudioVerseApi.demoStory,
            api: api,
            audioController: audio,
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Tín hiệu lúc nửa đêm'), findsOneWidget);
      expect(audio.loadedUrls.last, endsWith('/api/v1/audio/s0.mp3'));

      await tester.ensureVisible(find.text('Lần theo dấu chân về kho'));
      await tester.tap(find.text('Lần theo dấu chân về kho'));
      await tester.pumpAndSettle();
      expect(find.text('Trong kho thiết bị'), findsOneWidget);
      expect(audio.loadedUrls.last, endsWith('/api/v1/audio/s1.mp3'));

      await tester.ensureVisible(find.text('Giữ chìa khóa B'));
      await tester.tap(find.text('Giữ chìa khóa B'));
      await tester.pumpAndSettle();
      expect(find.text('Cánh cửa phía dưới'), findsOneWidget);
      expect(
        find.text('◆ An cảm thấy chiếc chìa khóa B trong túi áo.'),
        findsOneWidget,
      );

      await tester.ensureVisible(
        find.text('Mở cửa tầng hầm bằng chìa khóa B'),
      );
      await tester.tap(find.text('Mở cửa tầng hầm bằng chìa khóa B'));
      await tester.pumpAndSettle();
      expect(find.text('Kết thúc: Hồ sơ còn lại'), findsOneWidget);
      expect(find.text('Bạn đã đến một kết cục.'), findsOneWidget);
      expect(find.text('Chơi lại từ đầu'), findsOneWidget);
    },
  );

  testWidgets(
    'Uncertain transport failure retains idempotency key on retry',
    (WidgetTester tester) async {
      final api = FakeAudioVerseApi()..failNextChoiceWithTransportError = true;
      final audio = FakeSceneAudioController();

      await tester.pumpWidget(
        MaterialApp(
          home: StoryScreen(
            story: FakeAudioVerseApi.demoStory,
            api: api,
            audioController: audio,
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.ensureVisible(find.text('Lần theo dấu chân về kho'));
      await tester.tap(find.text('Lần theo dấu chân về kho'));
      await tester.pumpAndSettle();

      expect(find.textContaining('SocketException'), findsOneWidget);
      expect(api.submittedIdempotencyKeys.length, 1);
      final firstKey = api.submittedIdempotencyKeys.first;

      await tester.ensureVisible(find.text('Lần theo dấu chân về kho'));
      await tester.tap(find.text('Lần theo dấu chân về kho'));
      await tester.pumpAndSettle();

      expect(api.submittedIdempotencyKeys.length, 2);
      expect(api.submittedIdempotencyKeys[1], equals(firstKey));
      expect(find.text('Trong kho thiết bị'), findsOneWidget);
    },
  );

  testWidgets(
    'Committed choice followed by audio failure keeps new run and retries audio',
    (WidgetTester tester) async {
      final api = FakeAudioVerseApi();
      final audio = FakeSceneAudioController()
        ..failUrlsOnce.add(api.sceneAudioUrl('s1'));

      await tester.pumpWidget(
        MaterialApp(
          home: StoryScreen(
            story: FakeAudioVerseApi.demoStory,
            api: api,
            audioController: audio,
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.ensureVisible(find.text('Lần theo dấu chân về kho'));
      await tester.tap(find.text('Lần theo dấu chân về kho'));
      await tester.pumpAndSettle();

      expect(find.text('Trong kho thiết bị'), findsOneWidget);
      expect(
        find.textContaining('Đã lưu tiến trình nhưng chưa tải được âm thanh'),
        findsOneWidget,
      );
      expect(find.text('Thử tải lại âm thanh'), findsOneWidget);

      await tester.tap(find.text('Thử tải lại âm thanh'));
      await tester.pumpAndSettle();

      expect(
        find.textContaining('Đã lưu tiến trình nhưng chưa tải được âm thanh'),
        findsNothing,
      );
      expect(audio.loadedUrls.last, endsWith('/api/v1/audio/s1.mp3'));

      await tester.ensureVisible(find.text('Giữ chìa khóa B'));
      await tester.tap(find.text('Giữ chìa khóa B'));
      await tester.pumpAndSettle();
      expect(api.submittedExpectedVersions.last, equals(1));
      expect(find.text('Cánh cửa phía dưới'), findsOneWidget);
    },
  );

  testWidgets(
    '409 version conflict refreshes canonical run state from server',
    (WidgetTester tester) async {
      final api = FakeAudioVerseApi()..failNextChoiceWith409 = true;
      final audio = FakeSceneAudioController();

      await tester.pumpWidget(
        MaterialApp(
          home: StoryScreen(
            story: FakeAudioVerseApi.demoStory,
            api: api,
            audioController: audio,
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.ensureVisible(find.text('Lần theo dấu chân về kho'));
      await tester.tap(find.text('Lần theo dấu chân về kho'));
      await tester.pumpAndSettle();

      expect(api.getRunCalls, equals(1));
      expect(
        find.textContaining('Phiên truyện đã thay đổi (409)'),
        findsOneWidget,
      );
      expect(find.text('Cánh cửa phía dưới'), findsOneWidget);
    },
  );

  testWidgets(
    'T005: Resumes saved run position/speed, clamps seek, handles interruptions, and enforces offline lease expiry',
    (WidgetTester tester) async {
      var fakeNow = DateTime.utc(2026, 11, 18, 1, 0);
      final api = FakeAudioVerseApi()
        ..offlineLeaseExpiresAt = DateTime.utc(2026, 11, 18, 2, 0)
        ..continueListeningRuns = <StoryRun>[
          StoryRun(
            id: 'run-resumed-1',
            storyId: FakeAudioVerseApi.demoStory.id,
            version: 1,
            positionMs: 12000,
            playbackSpeed: 1.5,
            scene: FakeAudioVerseApi.scenes['s1']!,
          ),
        ];
      final audio = FakeSceneAudioController();

      await tester.pumpWidget(
        MaterialApp(
          home: StoryScreen(
            story: FakeAudioVerseApi.demoStory,
            api: api,
            audioController: audio,
            nowProvider: () => fakeNow,
          ),
        ),
      );
      await tester.pumpAndSettle();

      // 1. Resumed s1 at 12,000ms and 1.5x speed without silent autoplay (PLY-05, PLY-08, PLY-14)
      expect(find.text('Trong kho thiết bị'), findsOneWidget);
      expect(audio.currentPosition, equals(const Duration(seconds: 12)));
      expect(audio.currentSpeed, equals(1.5));
      expect(audio.isPlaying, isFalse);

      // 2. Seek +10s advances to 22s; seek -10s x 3 clamps to 0s (PLY-07)
      await tester.tap(find.byTooltip('Tiến 10 giây'));
      await tester.pump();
      expect(audio.currentPosition, equals(const Duration(seconds: 22)));
      for (var i = 0; i < 3; i++) {
        await tester.tap(find.byTooltip('Lùi 10 giây'));
        await tester.pump();
      }
      expect(audio.currentPosition, equals(Duration.zero));

      // 3. Speed change to 1.25x persists to server (PLY-05, PLY-08)
      await tester.tap(find.text('1.25x'));
      await tester.pumpAndSettle();
      expect(audio.currentSpeed, equals(1.25));
      expect(api.savedSpeeds.last, equals(1.25));

      // 4. Audio interruption pauses active playback and resumes when interruption ends (PLY-13)
      await audio.play();
      expect(audio.isPlaying, isTrue);
      await audio.handleInterruption(begin: true);
      expect(audio.isPlaying, isFalse);
      await audio.handleInterruption(begin: false, shouldResume: true);
      expect(audio.isPlaying, isTrue);

      // 5. Offline lease download & license expiry enforcement (PLY-10)
      await tester.tap(find.text('Tải offline'));
      await tester.pumpAndSettle();
      expect(find.text('Đã tải offline'), findsOneWidget);

      // Advance clock past lease expiry (02:00 UTC -> 03:00 UTC) and reload audio
      fakeNow = DateTime.utc(2026, 11, 18, 3, 0);
      await tester.pumpWidget(
        MaterialApp(
          home: StoryScreen(
            story: FakeAudioVerseApi.demoStory,
            api: api,
            audioController: audio,
            nowProvider: () => fakeNow,
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Tải offline'), findsOneWidget);
    },
  );
}
