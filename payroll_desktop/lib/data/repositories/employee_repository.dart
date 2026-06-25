import '../../services/api_service.dart';
import '../../services/api_result.dart';
import '../../core/database/database_helper.dart';
import 'dart:convert';

class EmployeeRepository {
  final _dbHelper = DatabaseHelper();

  Future<ApiResult<dynamic>> getEmployees({bool showDeleted = false, int page = 1}) async {
    final response = await ApiService.getEmployees(showDeleted: showDeleted, page: page);
    
    if (response is ApiSuccess) {
      // Cache results locally
      var results = response.data is Map ? response.data['results'] : response.data;
      if (results is List) {
        await _dbHelper.clearTable('employees');
        await _dbHelper.insertBatch('employees', List<Map<String, dynamic>>.from(results));
      }
      return response;
    } else {
      // Offline fallback
      try {
        final localData = await _dbHelper.queryAll('employees');
        if (localData.isNotEmpty) {
          final mappedData = localData.map((e) {
            var map = Map<String, dynamic>.from(e);
            if (map['is_active'] != null) map['is_active'] = map['is_active'] == 1;
            return map;
          }).toList();
          
          if (!showDeleted) {
            mappedData.removeWhere((e) => e['deleted_at'] != null);
          }
          return ApiSuccess({'results': mappedData, 'next': null});
        }
      } catch (_) {}
      return response;
    }
  }

  Future<ApiResult<dynamic>> enrollEmployee(Map<String, dynamic> data) async {
    final response = await ApiService.enrollEmployee(data);
    if (response is ApiError) {
      await _dbHelper.insertMutation('/api/v1/payroll/employees/enroll/', 'POST', jsonEncode(data));
      return ApiSuccess({'message': 'Saved offline', 'employee_id': 'OFFLINE-NEW', 'username': data['username']});
    }
    return response;
  }

  Future<ApiResult<dynamic>> updateEmployee(int id, Map<String, dynamic> data) async {
    final response = await ApiService.updateEmployee(id, data);
    if (response is ApiError) {
      await _dbHelper.insertMutation('/api/v1/payroll/employees/$id/', 'PATCH', jsonEncode(data));
      return ApiSuccess({'message': 'Saved offline'});
    }
    return response;
  }

  Future<ApiResult<bool>> deleteEmployee(int id) async {
    final response = await ApiService.deleteEmployee(id);
    if (response is ApiError) {
      await _dbHelper.insertMutation('/api/v1/payroll/employees/$id/', 'DELETE', '{}');
      return ApiSuccess(true);
    }
    return response;
  }

  Future<ApiResult<bool>> restoreEmployee(int id) async {
    final response = await ApiService.restoreEmployee(id);
    if (response is ApiError) {
      await _dbHelper.insertMutation('/api/v1/payroll/employees/$id/restore/', 'POST', '{}');
      return ApiSuccess(true);
    }
    return response;
  }

  Future<ApiResult<dynamic>> getAuditLogs({int? targetUserId}) {
    return ApiService.getAuditLogs(targetUserId: targetUserId);
  }
}
