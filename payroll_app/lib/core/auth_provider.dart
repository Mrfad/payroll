import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'api_client.dart';

class AuthProvider with ChangeNotifier {
  final ApiClient _apiClient = ApiClient();
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  
  bool _isAuthenticated = false;
  bool _isLoading = false;
  bool _isInitializing = true;
  String? _errorMessage;

  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  bool get isInitializing => _isInitializing;
  String? get errorMessage => _errorMessage;

  Future<void> login(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.dio.post('token/', data: {
        'username': username,
        'password': password,
      });

      if (response.statusCode == 200) {
        final access = response.data['access'];
        final refresh = response.data['refresh'];
        
        await _storage.write(key: 'access_token', value: access);
        await _storage.write(key: 'refresh_token', value: refresh);
        
        _isAuthenticated = true;
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        _errorMessage = 'Invalid username or password';
      } else {
        _errorMessage = 'Failed to connect to server';
      }
      _isAuthenticated = false;
    } catch (e) {
      _errorMessage = 'An unexpected error occurred';
      _isAuthenticated = false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    final refreshToken = await _storage.read(key: 'refresh_token');
    if (refreshToken != null) {
      try {
        await _apiClient.dio.post('token/blacklist/', data: {
          'refresh': refreshToken,
        });
      } catch (e) {
        // Even if blacklisting fails (e.g. network error), we still want to log out locally.
        debugPrint('Failed to blacklist token: $e');
      }
    }

    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
    _isAuthenticated = false;
    notifyListeners();
  }

  Future<void> checkAuthStatus() async {
    _isInitializing = true;
    notifyListeners();
    
    final token = await _storage.read(key: 'access_token');
    if (token != null) {
      try {
        // Verify token with backend
        await _apiClient.dio.post('token/verify/', data: {'token': token});
        _isAuthenticated = true;
      } catch (e) {
        // If the token is invalid, clear storage and log out
        await _storage.delete(key: 'access_token');
        await _storage.delete(key: 'refresh_token');
        _isAuthenticated = false;
      }
    } else {
      _isAuthenticated = false;
    }
    
    _isInitializing = false;
    notifyListeners();
  }
}
