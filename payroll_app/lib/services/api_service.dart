import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb, debugPrint;
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'api_result.dart';

class AuthException implements Exception {
  final String message;
  AuthException(this.message);
  @override
  String toString() => message;
}

class ApiService {
  static String get baseUrl {
    const envUrl = String.fromEnvironment('API_BASE_URL');
    if (envUrl.isNotEmpty) return envUrl;
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    return 'http://127.0.0.1:8000';
  }
  static const storage = FlutterSecureStorage();

  static Future<String?> _getValidAccessToken() async {
    return await storage.read(key: 'access_token');
  }

  static Future<bool> _tryRefreshToken() async {
    final refreshToken = await storage.read(key: 'refresh_token');
    if (refreshToken == null) return false;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/token/refresh/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': refreshToken}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await storage.write(key: 'access_token', value: data['access']);
        return true;
      }
    } catch (_) {}
    return false;
  }

  static Future<http.Response> _authenticatedRequest(
    String method, String url, {Map<String, dynamic>? body}) async {
    
    final token = await _getValidAccessToken();
    if (token == null) throw AuthException('Not authenticated');

    String clientPlatform = 'Unknown';
    try {
      if (kIsWeb) {
        clientPlatform = 'Web App';
      } else if (Platform.isWindows || Platform.isLinux || Platform.isMacOS) {
        clientPlatform = 'Desktop App';
      } else if (Platform.isAndroid || Platform.isIOS) {
        clientPlatform = 'Mobile App';
      }
    } catch (_) {}

    final headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
      'X-Client-Platform': clientPlatform,
    };

    http.Response response;
    switch (method) {
      case 'GET': response = await http.get(Uri.parse(url), headers: headers); break;
      case 'POST': response = await http.post(Uri.parse(url), headers: headers, body: body != null ? jsonEncode(body) : null); break;
      case 'PATCH': response = await http.patch(Uri.parse(url), headers: headers, body: body != null ? jsonEncode(body) : null); break;
      case 'DELETE': response = await http.delete(Uri.parse(url), headers: headers); break;
      default: throw Exception('Unsupported method');
    }

    if (response.statusCode == 401) {
      final refreshed = await _tryRefreshToken();
      if (refreshed) {
        return _authenticatedRequest(method, url, body: body);
      }
      // If refresh fails, clear storage
      await storage.delete(key: 'access_token');
      await storage.delete(key: 'refresh_token');
      throw AuthException('Session expired');
    }
    return response;
  }

  // LOGIN
  static Future<ApiResult<dynamic>> login(String username, String password) async {
    try {
      final url = Uri.parse('$baseUrl/api/v1/token/');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await storage.write(key: 'access_token', value: data['access']);
        await storage.write(key: 'refresh_token', value: data['refresh']);
        return ApiSuccess(data);
      }
      debugPrint('Login failed with status: \${response.statusCode}, body: \${response.body}');
      return ApiError('Login failed. Please check your credentials.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  // LOGOUT
  static Future<ApiResult<bool>> logout() async {
    try {
      final refreshToken = await storage.read(key: 'refresh_token');
      final accessToken = await storage.read(key: 'access_token');

      if (refreshToken != null && accessToken != null) {
        final url = Uri.parse('$baseUrl/api/v1/token/blacklist/');
        await http.post(
          url,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $accessToken',
          },
          body: jsonEncode({'refresh': refreshToken}),
        );
      }
      
      await storage.delete(key: 'access_token');
      await storage.delete(key: 'refresh_token');
      return const ApiSuccess(true);
    } catch (e) {
      await storage.delete(key: 'access_token');
      await storage.delete(key: 'refresh_token');
      return ApiError(e.toString());
    }
  }

  // USER PROFILE
  static Future<ApiResult<dynamic>> getUserProfile() async {
    try {
      final response = await _authenticatedRequest('GET', '$baseUrl/api/v1/payroll/user-profile/me/');
      if (response.statusCode == 200) {
        return ApiSuccess(jsonDecode(response.body));
      }
      return ApiError('Failed to fetch user profile.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  static Future<ApiResult<bool>> updateTheme(String theme) async {
    try {
      final response = await _authenticatedRequest('PATCH', '$baseUrl/api/v1/payroll/user-profile/me/', body: {'theme': theme});
      if (response.statusCode == 200) {
        return const ApiSuccess(true);
      }
      return ApiError('Failed to update theme.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  // EMPLOYEES CRUD
  static Future<ApiResult<dynamic>> getEmployees({bool showDeleted = false, int page = 1}) async {
    try {
      final query = '?page=$page${showDeleted ? "&show_deleted=true" : ""}';
      final response = await _authenticatedRequest('GET', '$baseUrl/api/v1/payroll/employees/$query');
      if (response.statusCode == 200) {
        return ApiSuccess(jsonDecode(response.body));
      }
      return ApiError('Failed to fetch employees.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  static Future<ApiResult<dynamic>> enrollEmployee(Map<String, dynamic> data) async {
    try {
      final response = await _authenticatedRequest('POST', '$baseUrl/api/v1/payroll/employees/enroll/', body: data);
      if (response.statusCode == 201 || response.statusCode == 200) {
        return ApiSuccess(jsonDecode(response.body));
      }
      return ApiError('Failed to enroll employee. ${response.body}', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  static Future<ApiResult<dynamic>> updateEmployee(int id, Map<String, dynamic> data) async {
    try {
      final response = await _authenticatedRequest('PATCH', '$baseUrl/api/v1/payroll/employees/$id/', body: data);
      if (response.statusCode == 200) {
        return ApiSuccess(jsonDecode(response.body));
      }
      return ApiError('Failed to update employee.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  static Future<ApiResult<bool>> deleteEmployee(int id) async {
    try {
      final response = await _authenticatedRequest('DELETE', '$baseUrl/api/v1/payroll/employees/$id/');
      if (response.statusCode == 204) {
        return const ApiSuccess(true);
      }
      return ApiError('Failed to delete employee.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  static Future<ApiResult<bool>> punchEmployee(int id, {String? direction}) async {
    try {
      final Map<String, dynamic> body = direction != null ? {'direction': direction} : {};
      final response = await _authenticatedRequest('POST', '$baseUrl/api/v1/payroll/employees/$id/punch/', body: body);
      if (response.statusCode == 201 || response.statusCode == 200) {
        return const ApiSuccess(true);
      }
      return ApiError('Failed to record punch.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  static Future<ApiResult<bool>> restoreEmployee(int id) async {
    try {
      final response = await _authenticatedRequest('POST', '$baseUrl/api/v1/payroll/employees/$id/restore/?show_deleted=true');
      if (response.statusCode == 200) {
        return const ApiSuccess(true);
      }
      return ApiError('Failed to restore employee.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  static Future<ApiResult<dynamic>> getAuditLogs({int? targetUserId}) async {
    try {
      var uri = '$baseUrl/api/v1/payroll/audit-logs/';
      if (targetUserId != null) {
        uri += '?target_user=$targetUserId';
      }
      final response = await _authenticatedRequest('GET', uri);
      if (response.statusCode == 200) {
        return ApiSuccess(json.decode(response.body));
      }
      return ApiError('Failed to fetch audit logs.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  // ATTENDANCE
  static Future<ApiResult<dynamic>> getAttendanceRecords({int page = 1, int? employeeId}) async {
    try {
      var url = '$baseUrl/api/v1/payroll/attendance-records/?page=$page';
      if (employeeId != null) {
        url += '&employee=$employeeId';
      }
      final response = await _authenticatedRequest('GET', url);
      if (response.statusCode == 200) {
        return ApiSuccess(jsonDecode(response.body));
      }
      return ApiError('Failed to fetch attendance records.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  // PAYROLL
  static Future<ApiResult<dynamic>> getPayrollEntries({int page = 1, int? employeeId}) async {
    try {
      var url = '$baseUrl/api/v1/payroll/payroll-entries/?page=$page';
      if (employeeId != null) {
        url += '&employee=$employeeId';
      }
      final response = await _authenticatedRequest('GET', url);
      if (response.statusCode == 200) {
        return ApiSuccess(jsonDecode(response.body));
      }
      return ApiError('Failed to fetch payroll entries.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  // REFS
  static Future<ApiResult<dynamic>> getCompanies() async {
    try {
      final response = await _authenticatedRequest('GET', '$baseUrl/api/v1/payroll/companies/');
      if (response.statusCode == 200) {
        return ApiSuccess(jsonDecode(response.body));
      }
      return ApiError('Failed to fetch companies.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  static Future<ApiResult<dynamic>> getDepartments() async {
    try {
      final response = await _authenticatedRequest('GET', '$baseUrl/api/v1/payroll/departments/');
      if (response.statusCode == 200) {
        return ApiSuccess(jsonDecode(response.body));
      }
      return ApiError('Failed to fetch departments.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }

  // DASHBOARD
  static Future<ApiResult<dynamic>> getDashboardData() async {
    try {
      final response = await _authenticatedRequest('GET', '$baseUrl/api/v1/payroll/dashboard/');
      if (response.statusCode == 200) {
        return ApiSuccess(jsonDecode(response.body));
      }
      return ApiError('Failed to load dashboard data.', statusCode: response.statusCode);
    } catch (e) {
      return ApiError(e.toString());
    }
  }
}
