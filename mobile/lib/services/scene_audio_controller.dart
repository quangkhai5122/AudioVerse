import 'package:just_audio/just_audio.dart';

abstract class SceneAudioController {
  Stream<bool> get playingStream;
  Stream<Duration> get positionStream;
  Duration? get duration;
  Duration get position;
  double get speed;

  Future<void> stop();
  Future<void> setUrl(String url);
  Future<void> play();
  Future<void> pause();
  Future<void> seek(Duration position);
  Future<void> seekRelative(Duration offset);
  Future<void> setSpeed(double newSpeed);
  Future<void> handleInterruption({
    required bool begin,
    bool shouldResume = true,
  });
  void dispose();
}

class JustAudioSceneController implements SceneAudioController {
  JustAudioSceneController({AudioPlayer? player})
    : _player = player ?? AudioPlayer();

  final AudioPlayer _player;
  double _speed = 1.0;
  bool _pausedByInterruption = false;

  @override
  Stream<bool> get playingStream => _player.playingStream;

  @override
  Stream<Duration> get positionStream => _player.positionStream;

  @override
  Duration? get duration => _player.duration;

  @override
  Duration get position => _player.position;

  @override
  double get speed => _speed;

  @override
  Future<void> stop() async {
    _pausedByInterruption = false;
    await _player.stop();
  }

  @override
  Future<void> setUrl(String url) async {
    await _player.setUrl(url);
  }

  @override
  Future<void> play() async {
    _pausedByInterruption = false;
    await _player.play();
  }

  @override
  Future<void> pause() async {
    _pausedByInterruption = false;
    await _player.pause();
  }

  @override
  Future<void> seek(Duration target) async {
    final maxDur = duration;
    var clamped = target < Duration.zero ? Duration.zero : target;
    if (maxDur != null && maxDur > Duration.zero && clamped > maxDur) {
      clamped = maxDur;
    }
    await _player.seek(clamped);
  }

  @override
  Future<void> seekRelative(Duration offset) async {
    await seek(position + offset);
  }

  @override
  Future<void> setSpeed(double newSpeed) async {
    final clamped = newSpeed.clamp(0.8, 2.0).toDouble();
    _speed = clamped;
    await _player.setSpeed(clamped);
  }

  @override
  Future<void> handleInterruption({
    required bool begin,
    bool shouldResume = true,
  }) async {
    if (begin) {
      if (_player.playing) {
        await _player.pause();
        _pausedByInterruption = true;
      }
      return;
    }
    if (_pausedByInterruption && shouldResume) {
      _pausedByInterruption = false;
      await _player.play();
    } else {
      _pausedByInterruption = false;
    }
  }

  @override
  void dispose() {
    _player.dispose();
  }
}
