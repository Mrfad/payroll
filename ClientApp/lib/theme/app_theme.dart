import 'package:flutter/material.dart';

class AppTheme {
  static final ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF1E3C72),
      brightness: Brightness.light,
      primary: const Color(0xFF1E3C72),
      secondary: const Color(0xFF2A5298),
      surface: Colors.white,
    ),
    scaffoldBackgroundColor: const Color(0xFFF1F5F9),
    cardColor: Colors.white,
    fontFamily: 'Roboto',
  );

  static final ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF1E3C72),
      brightness: Brightness.dark,
      primary: const Color(0xFF3B82F6),
      secondary: const Color(0xFF60A5FA),
      surface: const Color(0xFF1E293B),
    ),
    scaffoldBackgroundColor: const Color(0xFF0F172A),
    cardColor: const Color(0xFF1E293B),
    fontFamily: 'Roboto',
  );
}
