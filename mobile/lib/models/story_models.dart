class StorySummary {
  const StorySummary({required this.id, required this.title, required this.description, required this.genre});
  final String id;
  final String title;
  final String description;
  final String genre;
  factory StorySummary.fromJson(Map<String, dynamic> json) => StorySummary(
    id: json['id'] as String, title: json['title'] as String,
    description: json['description'] as String, genre: json['genre'] as String,
  );
}

class StoryChoice {
  const StoryChoice({required this.id, required this.label});
  final String id;
  final String label;
  factory StoryChoice.fromJson(Map<String, dynamic> json) => StoryChoice(
    id: json['id'] as String, label: json['label'] as String,
  );
}

class SceneInfo {
  const SceneInfo({required this.id, required this.title, required this.text,
      required this.choices, required this.memoryNotes, required this.ending});
  final String id;
  final String title;
  final String text;
  final List<StoryChoice> choices;
  final List<String> memoryNotes;
  final bool ending;
  factory SceneInfo.fromJson(Map<String, dynamic> json) => SceneInfo(
    id: json['id'] as String, title: json['title'] as String, text: json['text'] as String,
    choices: (json['choices'] as List<dynamic>).map((v) => StoryChoice.fromJson(v as Map<String,dynamic>)).toList(),
    memoryNotes: (json['memory_notes'] as List<dynamic>).cast<String>(), ending: json['ending'] as bool,
  );
}

class StoryRun {
  const StoryRun({required this.id, required this.storyId, required this.version, required this.scene});
  final String id;
  final String storyId;
  final int version;
  final SceneInfo scene;
  factory StoryRun.fromJson(Map<String, dynamic> json) => StoryRun(
    id: json['run_id'] as String, storyId: json['story_id'] as String,
    version: json['version'] as int, scene: SceneInfo.fromJson(json['scene'] as Map<String,dynamic>),
  );
}
