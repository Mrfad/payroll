import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000'; // Change if your Django port is different
  static const storage = FlutterSecureStorage();

  // LOGIN
  static Future<Map<String, dynamic>?> login(String username, String password) async {
    final url = Uri.parse('$baseUrl/api/v1/token/');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // Save tokens securely
      await storage.write(key: 'access_token', value: data['access']);
      await storage.write(key: 'refresh_token', value: data['refresh']);
      return data;
    } else {
      return null; // Login failed
    }
  }

  // LOGOUT (Blacklist the refresh token)
  static Future<bool> logout() async {
    final refreshToken = await storage.read(key: 'refresh_token');
    final accessToken = await storage.read(key: 'access_token');

    if (refreshToken == null || accessToken == null) return false;

    final url = Uri.parse('$baseUrl/api/v1/token/blacklist/');
    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $accessToken',
      },
      body: jsonEncode({'refresh': refreshToken}),
    );

    // Clear storage regardless of API response (force client-side logout)
    await storage.delete(key: 'access_token');
    await storage.delete(key: 'refresh_token');
    
    return response.statusCode == 200;
  }
}