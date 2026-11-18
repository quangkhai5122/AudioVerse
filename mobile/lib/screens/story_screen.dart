import 'dart:async';
import 'dart:math';
// ignore: deprecated_member_use
import 'package:flutter/material.dart';
import '../models/story_models.dart';
import '../services/api_client.dart';
import '../services/scene_audio_controller.dart';

class StoryScreen extends StatefulWidget {
  const StoryScreen({
    required this.story,
    super.key,
    this.api,
    this.audioController,
    this.resumeLatestOnStart = true,
    this.nowProvider,
  });

  final StorySummary story;
  final AudioVerseApi? api;
  final SceneAudioController? audioController;
  final bool resumeLatestOnStart;
  final DateTime Function()? nowProvider;

  @override
  State<StoryScreen> createState() => _StoryScreenState();
}

class _StoryScreenState extends State<StoryScreen>
    with WidgetsBindingObserver {
  static const List<double> _speedOptions = <double>[0.8, 1.0, 1.25, 1.5, 2.0];

  late final AudioVerseApi _api;
  late final bool _ownsApi;
  late final SceneAudioController _player;
  StoryRun? _run;
  String? _error;
  bool _busy = true;
  bool _audioLoadFailed = false;
  double _playbackSpeed = 1.0;

  Timer? _sleepTimer;
  int? _sleepTimerMinutes;
  final Map<String, OfflineSceneLease> _offlineLeases =
      <String, OfflineSceneLease>{};

  String? _pendingChoiceId;
  int? _pendingVersion;
  String? _pendingKey;

  DateTime _now() => (widget.nowProvider?.call() ?? DateTime.now()).toUtc();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _ownsApi = widget.api == null;
    _api = widget.api ?? AudioVerseApi();
    _player = widget.audioController ?? JustAudioSceneController();
    _initOrResumeRun();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _sleepTimer?.cancel();
    _player.dispose();
    if (_ownsApi) {
      _api.dispose();
    }
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.paused ||
        state == AppLifecycleState.inactive) {
      unawaited(_syncProgress());
    }
  }

  void _clearPendingChoice() {
    _pendingChoiceId = null;
    _pendingVersion = null;
    _pendingKey = null;
  }

  Future<void> _initOrResumeRun() async {
    if (widget.resumeLatestOnStart) {
      try {
        final recent = await _api.continueListening();
        final match = recent
            .where((r) => r.storyId == widget.story.id && !r.scene.ending)
            .firstOrNull;
        if (match != null) {
          _playbackSpeed = match.playbackSpeed.clamp(0.8, 2.0).toDouble();
          await _applyRunAndLoadAudio(
            match,
            restorePositionMs: match.positionMs,
          );
          return;
        }
      } catch (_) {
        // Fallback to starting a fresh run if continue-listening is unavailable.
      }
    }
    await _begin();
  }

  Future<void> _begin() async {
    setState(() {
      _busy = true;
      _error = null;
      _audioLoadFailed = false;
      _clearPendingChoice();
    });
    try {
      final run = await _api.begin(widget.story.id);
      await _applyRunAndLoadAudio(run);
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = '$e';
          _busy = false;
        });
      }
    }
  }

  Future<String> _resolveAudioUrlForScene(String sceneId) async {
    final lease = _offlineLeases[sceneId];
    if (lease != null) {
      if (!lease.isUsableAt(_now())) {
        _offlineLeases.remove(sceneId);
        throw Exception(
          'Bản tải offline của cảnh $sceneId đã hết hạn hoặc bị thu hồi bản quyền.',
        );
      }
      final validOnServer = await _api.validateOfflineLease(lease.leaseId);
      if (!validOnServer) {
        _offlineLeases.remove(sceneId);
        throw Exception(
          'Bản tải offline của cảnh $sceneId không còn hiệu lực bản quyền.',
        );
      }
      return _api.resolveMediaUrl(lease.downloadUrl);
    }
    return _api.sceneAudioUrl(sceneId);
  }

  /// Commits [run] to UI state BEFORE loading scene audio so a failed audio load
  /// never leaves a stale [_run] version after a server transition has committed.
  Future<void> _applyRunAndLoadAudio(
    StoryRun run, {
    String? noticeMessage,
    int restorePositionMs = 0,
  }) async {
    if (mounted) {
      setState(() {
        _run = run;
        _error = noticeMessage;
        _audioLoadFailed = false;
      });
    }
    try {
      await _player.stop();
      final url = await _resolveAudioUrlForScene(run.scene.id);
      await _player.setUrl(url);
      await _player.setSpeed(_playbackSpeed);
      if (restorePositionMs > 0) {
        await _player.seek(Duration(milliseconds: restorePositionMs));
      }
      if (mounted) {
        setState(() {
          _busy = false;
          _audioLoadFailed = false;
        });
      }
    } catch (audioErr) {
      if (mounted) {
        setState(() {
          _busy = false;
          _audioLoadFailed = true;
          final prefix = noticeMessage != null ? '$noticeMessage\n' : '';
          _error =
              '$prefixĐã lưu tiến trình nhưng chưa tải được âm thanh: $audioErr';
        });
      }
    }
  }

  Future<void> _syncProgress() async {
    final run = _run;
    if (run == null) {
      return;
    }
    try {
      final updated = await _api.saveProgress(
        run,
        positionMs: _player.position.inMilliseconds,
        playbackSpeed: _playbackSpeed,
      );
      if (mounted) {
        setState(() {
          _run = updated;
        });
      }
    } catch (_) {
      // Non-fatal in background/pause write-back.
    }
  }

  Future<void> _togglePlayPause(bool isPlaying) async {
    if (isPlaying) {
      await _player.pause();
      await _syncProgress();
    } else {
      await _player.play();
    }
  }

  Future<void> _changeSpeed(double newSpeed) async {
    final clamped = newSpeed.clamp(0.8, 2.0).toDouble();
    await _player.setSpeed(clamped);
    if (mounted) {
      setState(() {
        _playbackSpeed = clamped;
      });
    }
    await _syncProgress();
  }

  void _configureSleepTimer(int? minutes, {Duration? overrideDuration}) {
    _sleepTimer?.cancel();
    setState(() {
      _sleepTimerMinutes = minutes;
    });
    if (minutes == null || minutes <= 0) {
      return;
    }
    final dur = overrideDuration ?? Duration(minutes: minutes);
    _sleepTimer = Timer(dur, () async {
      await _player.pause();
      await _syncProgress();
      if (mounted) {
        setState(() {
          _sleepTimerMinutes = null;
          _error = 'Hẹn giờ ngủ đã dừng phát và lưu vị trí nghe.';
        });
      }
    });
  }

  Future<void> _downloadCurrentSceneOffline() async {
    final run = _run;
    if (_busy || run == null) {
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final lease = await _api.createOfflineLease(
        widget.story.id,
        run.scene.id,
      );
      if (mounted) {
        setState(() {
          _offlineLeases[run.scene.id] = lease;
          _busy = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Không thể tải offline: $e';
          _busy = false;
        });
      }
    }
  }

  Future<void> _retryAudio() async {
    final run = _run;
    if (_busy || run == null) {
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    await _applyRunAndLoadAudio(run, restorePositionMs: run.positionMs);
  }

  String _newKey() {
    final r = Random.secure();
    return List.generate(24, (_) => r.nextInt(16).toRadixString(16)).join();
  }

  String _keyForChoice(StoryRun run, String choiceId) {
    if (_pendingChoiceId == choiceId &&
        _pendingVersion == run.version &&
        _pendingKey != null) {
      return _pendingKey!;
    }
    final key = _newKey();
    _pendingChoiceId = choiceId;
    _pendingVersion = run.version;
    _pendingKey = key;
    return key;
  }

  Future<void> _choose(StoryChoice choice) async {
    final currentRun = _run;
    if (_busy || currentRun == null) {
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    final idemKey = _keyForChoice(currentRun, choice.id);
    try {
      final newRun = await _api.choose(currentRun, choice.id, idemKey);
      _clearPendingChoice();
      await _applyRunAndLoadAudio(newRun);
    } on ApiException catch (e) {
      _clearPendingChoice();
      if (e.statusCode == 409) {
        try {
          final refreshed = await _api.getRun(currentRun.id);
          await _applyRunAndLoadAudio(
            refreshed,
            noticeMessage:
                'Phiên truyện đã thay đổi (409); đã đồng bộ trạng thái mới nhất.',
            restorePositionMs: refreshed.positionMs,
          );
          return;
        } catch (refreshErr) {
          if (mounted) {
            setState(() {
              _error =
                  'Xung đột phiên bản (409) và không thể đồng bộ lại: $refreshErr';
              _busy = false;
            });
          }
          return;
        }
      }
      if (mounted) {
        setState(() {
          _error = '$e';
          _busy = false;
        });
      }
    } catch (e) {
      // Transport/timeout error: retain pending idempotency key for safe retry.
      if (mounted) {
        setState(() {
          _error = '$e';
          _busy = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final run = _run;
    final currentLease = run != null ? _offlineLeases[run.scene.id] : null;
    final hasValidOffline =
        currentLease != null && currentLease.isUsableAt(_now());

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.story.title),
        backgroundColor: Colors.transparent,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
            Text(
              widget.story.attribution,
              style: const TextStyle(
                fontSize: 11,
                color: Colors.white60,
                letterSpacing: 1,
              ),
            ),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _error!,
                      style: const TextStyle(color: Colors.orangeAccent),
                    ),
                    if (_audioLoadFailed)
                      TextButton(
                        onPressed: _busy ? null : _retryAudio,
                        child: const Text('Thử tải lại âm thanh'),
                      ),
                  ],
                ),
              ),
            if (run == null)
              Center(
                child: _busy
                    ? const CircularProgressIndicator()
                    : FilledButton(
                        onPressed: _begin,
                        child: const Text('Thử lại'),
                      ),
              ),
            if (run != null) ...[
              const SizedBox(height: 18),
              Text(
                run.scene.title,
                style: const TextStyle(
                  fontSize: 27,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 14),
              Text(
                run.scene.text,
                style: const TextStyle(fontSize: 17, height: 1.7),
              ),
              for (final note in run.scene.memoryNotes)
                Padding(
                  padding: const EdgeInsets.only(top: 10),
                  child: Text(
                    '◆ $note',
                    style: const TextStyle(color: Color(0xFFE5BC7B)),
                  ),
                ),
              const SizedBox(height: 24),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(15),
                  child: Column(
                    children: [
                      const Text('Giọng đọc demo · eSpeak'),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          IconButton(
                            tooltip: 'Lùi 10 giây',
                            onPressed: _busy
                                ? null
                                : () => _player.seekRelative(
                                    const Duration(seconds: -10),
                                  ),
                            icon: const Icon(Icons.replay_10),
                          ),
                          const SizedBox(width: 8),
                          StreamBuilder<bool>(
                            stream: _player.playingStream,
                            builder: (context, snapshot) =>
                                IconButton.filledTonal(
                                  iconSize: 30,
                                  onPressed: _busy
                                      ? null
                                      : () => _togglePlayPause(
                                          snapshot.data == true,
                                        ),
                                  icon: Icon(
                                    snapshot.data == true
                                        ? Icons.pause
                                        : Icons.play_arrow,
                                  ),
                                ),
                          ),
                          const SizedBox(width: 8),
                          IconButton(
                            tooltip: 'Tiến 10 giây',
                            onPressed: _busy
                                ? null
                                : () => _player.seekRelative(
                                    const Duration(seconds: 10),
                                  ),
                            icon: const Icon(Icons.forward_10),
                          ),
                        ],
                      ),
                      StreamBuilder<Duration>(
                        stream: _player.positionStream,
                        builder: (context, snapshot) {
                          final duration = _player.duration ?? Duration.zero;
                          final max = duration.inMilliseconds.toDouble();
                          final value =
                              (snapshot.data ?? _player.position)
                                  .inMilliseconds
                                  .toDouble()
                                  .clamp(0.0, max > 0 ? max : 1.0)
                                  .toDouble();
                          return Slider(
                            value: value,
                            max: max > 0 ? max : 1,
                            onChanged: max > 0
                                ? (v) => _player.seek(
                                    Duration(milliseconds: v.toInt()),
                                  )
                                : null,
                          );
                        },
                      ),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        alignment: WrapAlignment.center,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          for (final spd in _speedOptions)
                            ChoiceChip(
                              label: Text('${spd}x'),
                              selected: _playbackSpeed == spd,
                              onSelected: _busy
                                  ? null
                                  : (_) => _changeSpeed(spd),
                            ),
                          TextButton.icon(
                            onPressed: _busy
                                ? null
                                : () => _configureSleepTimer(
                                    _sleepTimerMinutes == null ? 15 : null,
                                  ),
                            icon: const Icon(Icons.bedtime_outlined, size: 18),
                            label: Text(
                              _sleepTimerMinutes == null
                                  ? 'Hẹn giờ ngủ'
                                  : 'Hẹn giờ: $_sleepTimerMinutes phút',
                            ),
                          ),
                          TextButton.icon(
                            onPressed: _busy
                                ? null
                                : _downloadCurrentSceneOffline,
                            icon: Icon(
                              hasValidOffline
                                  ? Icons.offline_pin
                                  : Icons.download_for_offline_outlined,
                              size: 18,
                            ),
                            label: Text(
                              hasValidOffline
                                  ? 'Đã tải offline'
                                  : 'Tải offline',
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 14),
              if (!run.scene.ending)
                const Text(
                  'Bạn muốn làm gì?',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
              const SizedBox(height: 8),
              for (final choice in run.scene.choices)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: OutlinedButton(
                    onPressed: _busy ? null : () => _choose(choice),
                    child: Padding(
                      padding: const EdgeInsets.all(10),
                      child: Text(choice.label),
                    ),
                  ),
                ),
              if (run.scene.ending) ...[
                const Text(
                  'Bạn đã đến một kết cục.',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 10),
                FilledButton(
                  onPressed: _busy ? null : _begin,
                  child: const Text('Chơi lại từ đầu'),
                ),
              ],
              if (_busy) const LinearProgressIndicator(),
            ],
          ],
          ),
        ),
      ),
    );
  }
}
