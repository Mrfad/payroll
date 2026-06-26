import '../../services/api_service.dart';
import '../../services/api_result.dart';

class DashboardRepository {
  Future<ApiResult<dynamic>> getDashboardData() {
    return ApiService.getDashboardData();
  }
}
