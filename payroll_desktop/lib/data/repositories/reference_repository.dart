import '../../services/api_service.dart';
import '../../services/api_result.dart';
import '../../core/database/database_helper.dart';

class ReferenceRepository {
  final _dbHelper = DatabaseHelper();

  Future<ApiResult<dynamic>> getCompanies() async {
    final response = await ApiService.getCompanies();
    if (response is ApiSuccess) {
      if (response.data is List) {
        await _dbHelper.clearTable('companies');
        await _dbHelper.insertBatch('companies', List<Map<String, dynamic>>.from(response.data));
      }
      return response;
    } else {
      try {
        final localData = await _dbHelper.queryAll('companies');
        if (localData.isNotEmpty) return ApiSuccess(localData);
      } catch (_) {}
      return response;
    }
  }

  Future<ApiResult<dynamic>> getDepartments() async {
    final response = await ApiService.getDepartments();
    if (response is ApiSuccess) {
      if (response.data is List) {
        await _dbHelper.clearTable('departments');
        await _dbHelper.insertBatch('departments', List<Map<String, dynamic>>.from(response.data));
      }
      return response;
    } else {
      try {
        final localData = await _dbHelper.queryAll('departments');
        if (localData.isNotEmpty) return ApiSuccess(localData);
      } catch (_) {}
      return response;
    }
  }
}
