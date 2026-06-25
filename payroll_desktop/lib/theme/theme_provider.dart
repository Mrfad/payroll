import 'package:flutter/material.dart';
import '../services/api_result.dart';
import '../core/di/injection.dart';
import '../data/repositories/auth_repository.dart';

class ThemeProvider with ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.light;

  ThemeMode get themeMode => _themeMode;

  bool get isDarkMode => _themeMode == ThemeMode.dark;

  Future<void> fetchTheme() async {
    try {
      final profile = await getIt<AuthRepository>().getUserProfile();
      if (profile is ApiSuccess && profile.data.containsKey('theme')) {
        _themeMode = profile.data['theme'] == 'dark' ? ThemeMode.dark : ThemeMode.light;
        notifyListeners();
      }
    } catch (e) {
      debugPrint("Error fetching theme: $e");
    }
  }

  Future<void> toggleTheme(bool isDark) async {
    _themeMode = isDark ? ThemeMode.dark : ThemeMode.light;
    notifyListeners();
    
    try {
      await getIt<AuthRepository>().updateTheme(isDark ? 'dark' : 'light');
    } catch (e) {
      debugPrint("Error updating theme: $e");
    }
  }
}
