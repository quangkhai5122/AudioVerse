import 'package:flutter/material.dart';
import 'screens/catalog_screen.dart';

void main() => runApp(const AudioVerseApp());

class AudioVerseApp extends StatelessWidget {
  const AudioVerseApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'AudioVerse', debugShowCheckedModeBanner: false,
    theme: ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF67D8C4),
          brightness: Brightness.dark, surface: const Color(0xFF151E31)),
      scaffoldBackgroundColor: const Color(0xFF0D1220),
    ),
    home: const CatalogScreen(),
  );
}
