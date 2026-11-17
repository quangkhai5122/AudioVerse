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
  });

  final StorySummary story;
  final AudioVerseApi? api;
  final SceneAudioController? audioController;

  @override
  State<StoryScreen> createState() => _StoryScreenState();
}

class _StoryScreenState extends State<StoryScreen> {
  late final AudioVerseApi _api;
  late final bool _ownsApi;
  late final SceneAudioController _player;
  StoryRun? _run;
  String? _error;
  bool _busy = true;
  bool _audioLoadFailed = false;

  String? _pendingChoiceId;
  int? _pendingVersion;
  String? _pendingKey;

  @override
  void initState() {
    super.initState();
    _ownsApi = widget.api == null;
    _api = widget.api ?? AudioVerseApi();
    _player = widget.audioController ?? JustAudioSceneController();
    _begin();
  }

  @override
  void dispose() {
    _player.dispose();
    if (_ownsApi) {
      _api.dispose();
    }
    super.dispose();
  }

  void _clearPendingChoice() {
    _pendingChoiceId = null;
    _pendingVersion = null;
    _pendingKey = null;
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

  /// Commits [run] to UI state BEFORE loading scene audio so a failed audio load
  /// never leaves a stale [_run] version after a server transition has committed.
  Future<void> _applyRunAndLoadAudio(
    StoryRun run, {
    String? noticeMessage,
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
      await _player.setUrl(_api.sceneAudioUrl(run.scene.id));
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

  Future<void> _retryAudio() async {
    final run = _run;
    if (_busy || run == null) {
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    await _applyRunAndLoadAudio(run);
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
          );
          return;
        } catch (refreshErr) {
          if (mounted) {
            setState(() {
              _error = 'Xung đột phiên bản (409) và không thể đồng bộ lại: $refreshErr';
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
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.story.title),
        backgroundColor: Colors.transparent,
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            const Text(
              'BẢN CHẠY DEMO · GIỌNG TỔNG HỢP',
              style: TextStyle(
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
                      const SizedBox(height: 5),
                      StreamBuilder<bool>(
                        stream: _player.playingStream,
                        builder: (context, snapshot) => IconButton.filledTonal(
                          iconSize: 30,
                          onPressed: _busy
                              ? null
                              : () => snapshot.data == true
                                    ? _player.pause()
                                    : _player.play(),
                          icon: Icon(
                            snapshot.data == true
                                ? Icons.pause
                                : Icons.play_arrow,
                          ),
                        ),
                      ),
                      StreamBuilder<Duration>(
                        stream: _player.positionStream,
                        builder: (context, snapshot) {
                          final duration = _player.duration ?? Duration.zero;
                          final max = duration.inMilliseconds.toDouble();
                          final value = (snapshot.data ?? Duration.zero)
                              .inMilliseconds
                              .toDouble()
                              .clamp(0.0, max)
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
    );
  }
}
