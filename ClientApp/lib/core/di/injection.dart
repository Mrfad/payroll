import 'package:get_it/get_it.dart';
import '../../services/api_service.dart';
import '../../services/websocket_service.dart';
import '../../data/repositories/auth_repository.dart';
import '../../data/repositories/employee_repository.dart';
import '../../data/repositories/reference_repository.dart';
import '../../data/repositories/dashboard_repository.dart';
import '../../providers/auth_provider.dart';
import '../../theme/theme_provider.dart';

final getIt = GetIt.instance;

void setupInjection() {
  // Providers
  getIt.registerLazySingleton<AuthProvider>(() => AuthProvider());
  getIt.registerLazySingleton<ThemeProvider>(() => ThemeProvider());

  // Services
  getIt.registerLazySingleton<ApiService>(() => ApiService());
  getIt.registerLazySingleton<WebSocketService>(() => WebSocketService());

  // Repositories
  getIt.registerLazySingleton<AuthRepository>(() => AuthRepository());
  getIt.registerLazySingleton<EmployeeRepository>(() => EmployeeRepository());
  getIt.registerLazySingleton<ReferenceRepository>(() => ReferenceRepository());
  getIt.registerLazySingleton<DashboardRepository>(() => DashboardRepository());
}
