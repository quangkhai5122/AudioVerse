// ignore: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'screens/catalog_screen.dart';
import 'services/api_client.dart';
import 'services/scene_audio_controller.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SemanticsBinding.instance.ensureSemantics();
  runApp(const AudioVerseApp());
}

class AudioVerseApp extends StatelessWidget {
  const AudioVerseApp({super.key, this.api, this.audioControllerBuilder});

  final AudioVerseApi? api;
  final SceneAudioController Function()? audioControllerBuilder;

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'AudioVerse',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF67D8C4),
        brightness: Brightness.dark,
        surface: const Color(0xFF151E31),
      ),
      scaffoldBackgroundColor: const Color(0xFF0D1220),
    ),
    home: CatalogScreen(
      api: api,
      audioControllerBuilder: audioControllerBuilder,
    ),
  );
}
