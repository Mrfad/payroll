import 'package:flutter/material.dart';
import '../services/api_result.dart';
import '../core/di/injection.dart';
import '../data/repositories/auth_repository.dart';
import '../services/websocket_service.dart';
import '../providers/auth_provider.dart';

class ThemeProvider with ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.light;

  ThemeMode get themeMode => _themeMode;

  ThemeProvider() {
    getIt<WebSocketService>().updates.listen((event) {
      if (event['model'] == 'userprofile' && event['action'] == 'theme_updated') {
        final authProvider = getIt<AuthProvider>();
        if (authProvider.userId != null && event['user_id'] == authProvider.userId) {
          _themeMode = event['theme'] == 'dark' ? ThemeMode.dark : ThemeMode.light;
          notifyListeners();
        }
      }
    });
  }

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
