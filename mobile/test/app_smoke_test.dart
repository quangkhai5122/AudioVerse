import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:audioverse/main.dart';

void main() {
  testWidgets('App displays product headline', (tester) async {
    await tester.pumpWidget(const AudioVerseApp());
    expect(find.textContaining('Một câu chuyện'), findsOneWidget);
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
