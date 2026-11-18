import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/story_models.dart';

class ApiException implements Exception {
  const ApiException(this.statusCode, this.message);
  final int statusCode;
  final String message;

  @override
  String toString() => 'HTTP $statusCode: $message';
}

class AudioVerseApi {
  AudioVerseApi({
    http.Client? client,
    this.timeout = const Duration(seconds: 10),
  }) : _client = client ?? http.Client();

  final http.Client _client;
  final Duration timeout;

  static const String baseUrl = String.fromEnvironment(
    'API_BASE',
    defaultValue: 'http://10.0.2.2:8765',
  );
  static const Map<String, String> _headers = {
    'Content-Type': 'application/json',
    // NOT identity authentication; demo-only. Production auth uses Bearer token.
    'X-Demo-Actor': 'demo-local',
  };

  Future<dynamic> _request(String path, {Map<String, dynamic>? post}) async {
    final url = Uri.parse('$baseUrl$path');
    final future = post == null
        ? _client.get(url, headers: _headers)
        : _client.post(url, headers: _headers, body: jsonEncode(post));
    final response = await future.timeout(timeout);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(
        response.statusCode,
        utf8.decode(response.bodyBytes),
      );
    }
    return jsonDecode(utf8.decode(response.bodyBytes));
  }

  Future<List<StorySummary>> catalog() async {
    final data = await _request('/api/v1/catalog') as List<dynamic>;
    return data
        .map((e) => StorySummary.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<StoryRun> begin(String storyId) async => StoryRun.fromJson(
    await _request('/api/v1/runs', post: {'story_id': storyId})
        as Map<String, dynamic>,
  );

  Future<StoryRun> getRun(String runId) async => StoryRun.fromJson(
    await _request('/api/v1/runs/$runId') as Map<String, dynamic>,
  );

  Future<List<StoryRun>> continueListening() async {
    final data =
        await _request('/api/v1/me/continue-listening') as List<dynamic>;
    return data
        .map((e) => StoryRun.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<StoryRun> saveProgress(
    StoryRun run, {
    required int positionMs,
    required double playbackSpeed,
  }) async => StoryRun.fromJson(
    await _request(
          '/api/v1/runs/${run.id}/progress',
          post: {
            'scene_id': run.scene.id,
            'position_ms': positionMs,
            'playback_speed': playbackSpeed,
          },
        )
        as Map<String, dynamic>,
  );

  Future<StoryRun> choose(
    StoryRun run,
    String choiceId,
    String idempotencyKey,
  ) async => StoryRun.fromJson(
    await _request(
          '/api/v1/runs/${run.id}/choices',
          post: {
            'choice_id': choiceId,
            'expected_version': run.version,
            'idempotency_key': idempotencyKey,
          },
        )
        as Map<String, dynamic>,
  );

  Future<OfflineSceneLease> createOfflineLease(
    String workId,
    String sceneId,
  ) async => OfflineSceneLease.fromJson(
    await _request(
          '/api/v1/downloads/leases',
          post: {'work_id': workId, 'scene_id': sceneId},
        )
        as Map<String, dynamic>,
  );

  Future<bool> validateOfflineLease(String leaseId) async {
    final data =
        await _request('/api/v1/downloads/leases/$leaseId/validate')
            as Map<String, dynamic>;
    return (data['valid'] as bool?) ?? false;
  }

  String sceneAudioUrl(String sceneId) => '$baseUrl/api/v1/audio/$sceneId.mp3';

  String resolveMediaUrl(String relativeOrFullUrl) =>
      relativeOrFullUrl.startsWith('http')
      ? relativeOrFullUrl
      : '$baseUrl$relativeOrFullUrl';

  void dispose() => _client.close();
}
