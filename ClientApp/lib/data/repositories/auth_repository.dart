import '../../services/api_service.dart';
import '../../services/api_result.dart';

class AuthRepository {
  Future<ApiResult<dynamic>> login(String username, String password) {
    return ApiService.login(username, password);
  }

  Future<ApiResult<bool>> logout() {
    return ApiService.logout();
  }

  Future<ApiResult<dynamic>> getUserProfile() {
    return ApiService.getUserProfile();
  }

  Future<ApiResult<bool>> updateTheme(String theme) {
    return ApiService.updateTheme(theme);
  }
}
