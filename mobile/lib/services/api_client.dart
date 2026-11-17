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
    // NOT identity authentication; demo-only. Production auth is pending.
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

  String sceneAudioUrl(String sceneId) => '$baseUrl/api/v1/audio/$sceneId.mp3';

  void dispose() => _client.close();
}
