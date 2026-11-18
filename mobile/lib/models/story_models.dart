class StorySummary {
  const StorySummary({
    required this.id,
    required this.title,
    required this.description,
    required this.genre,
    this.attribution = 'Tác phẩm gốc AudioVerse · Giọng tổng hợp kỹ thuật (eSpeak)',
    this.voiceLabel = 'synthetic_tts',
  });

  final String id;
  final String title;
  final String description;
  final String genre;
  final String attribution;
  final String voiceLabel;

  factory StorySummary.fromJson(Map<String, dynamic> json) => StorySummary(
    id: json['id'] as String,
    title: json['title'] as String,
    description: json['description'] as String,
    genre: json['genre'] as String,
    attribution:
        (json['attribution'] as String?) ??
        'Tác phẩm gốc AudioVerse · Giọng tổng hợp kỹ thuật (eSpeak)',
    voiceLabel: (json['voice_label'] as String?) ?? 'synthetic_tts',
  );
}

class StoryChoice {
  const StoryChoice({required this.id, required this.label});
  final String id;
  final String label;
  factory StoryChoice.fromJson(Map<String, dynamic> json) =>
      StoryChoice(id: json['id'] as String, label: json['label'] as String);
}

class SceneInfo {
  const SceneInfo({
    required this.id,
    required this.title,
    required this.text,
    required this.choices,
    required this.memoryNotes,
    required this.ending,
  });
  final String id;
  final String title;
  final String text;
  final List<StoryChoice> choices;
  final List<String> memoryNotes;
  final bool ending;
  factory SceneInfo.fromJson(Map<String, dynamic> json) => SceneInfo(
    id: json['id'] as String,
    title: json['title'] as String,
    text: json['text'] as String,
    choices: (json['choices'] as List<dynamic>)
        .map((v) => StoryChoice.fromJson(v as Map<String, dynamic>))
        .toList(),
    memoryNotes: (json['memory_notes'] as List<dynamic>).cast<String>(),
    ending: json['ending'] as bool,
  );
}

class StoryRun {
  const StoryRun({
    required this.id,
    required this.storyId,
    required this.version,
    required this.scene,
    this.editionId = 'ben-kia-canh-cua-ed1',
    this.positionMs = 0,
    this.playbackSpeed = 1.0,
  });

  final String id;
  final String storyId;
  final String editionId;
  final int version;
  final int positionMs;
  final double playbackSpeed;
  final SceneInfo scene;

  factory StoryRun.fromJson(Map<String, dynamic> json) => StoryRun(
    id: json['run_id'] as String,
    storyId: json['story_id'] as String,
    editionId: (json['edition_id'] as String?) ?? 'ben-kia-canh-cua-ed1',
    version: json['version'] as int,
    positionMs: (json['position_ms'] as num?)?.toInt() ?? 0,
    playbackSpeed: (json['playback_speed'] as num?)?.toDouble() ?? 1.0,
    scene: SceneInfo.fromJson(json['scene'] as Map<String, dynamic>),
  );
}

class OfflineSceneLease {
  const OfflineSceneLease({
    required this.leaseId,
    required this.sceneId,
    required this.editionId,
    required this.downloadUrl,
    required this.sha256,
    required this.byteSize,
    required this.transcript,
    required this.expiresAt,
    this.revoked = false,
  });

  final String leaseId;
  final String sceneId;
  final String editionId;
  final String downloadUrl;
  final String sha256;
  final int byteSize;
  final String transcript;
  final DateTime expiresAt;
  final bool revoked;

  bool isUsableAt(DateTime now) => !revoked && now.isBefore(expiresAt);

  factory OfflineSceneLease.fromJson(Map<String, dynamic> json) =>
      OfflineSceneLease(
        leaseId: json['lease_id'] as String,
        sceneId: json['scene_id'] as String,
        editionId: (json['edition_id'] as String?) ?? 'ben-kia-canh-cua-ed1',
        downloadUrl: json['download_url'] as String,
        sha256: json['sha256'] as String,
        byteSize: (json['byte_size'] as num).toInt(),
        transcript: (json['transcript'] as String?) ?? '',
        expiresAt: DateTime.parse(json['lease_expires_at'] as String).toUtc(),
      );
}
