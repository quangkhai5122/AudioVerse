import 'package:just_audio/just_audio.dart';

abstract class SceneAudioController {
  Stream<bool> get playingStream;
  Stream<Duration> get positionStream;
  Duration? get duration;

  Future<void> stop();
  Future<void> setUrl(String url);
  Future<void> play();
  Future<void> pause();
  Future<void> seek(Duration position);
  void dispose();
}

class JustAudioSceneController implements SceneAudioController {
  JustAudioSceneController({AudioPlayer? player})
    : _player = player ?? AudioPlayer();

  final AudioPlayer _player;

  @override
  Stream<bool> get playingStream => _player.playingStream;

  @override
  Stream<Duration> get positionStream => _player.positionStream;

  @override
  Duration? get duration => _player.duration;

  @override
  Future<void> stop() => _player.stop();

  @override
  Future<void> setUrl(String url) async {
    await _player.setUrl(url);
  }

  @override
  Future<void> play() => _player.play();

  @override
  Future<void> pause() => _player.pause();

  @override
  Future<void> seek(Duration position) => _player.seek(position);

  @override
  void dispose() {
    _player.dispose();
  }
}
