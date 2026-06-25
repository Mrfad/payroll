import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/api_result.dart';
import '../core/di/injection.dart';
import '../data/repositories/auth_repository.dart';

class AuthProvider with ChangeNotifier {
  List<String> _permissions = [];
  List<String> _groups = [];
  int? _userId;
  String? _username;
  int? _employeeId;

  List<String> get permissions => _permissions;
  int? get userId => _userId;
  String? get username => _username;
  int? get employeeId => _employeeId;

  bool hasPermission(String perm) => _permissions.contains(perm);
  bool get isManagerOrDeveloper => _groups.contains('Managers') || _groups.contains('Developers');

  bool canAddEmployee() => _permissions.contains('payroll.add_employee');
  bool canEditEmployee() => _permissions.contains('payroll.change_employee');
  bool canDeleteEmployee() => _permissions.contains('payroll.delete_employee');

  Future<void> loadPermissions() async {
    try {
      final profileResult = await getIt<AuthRepository>().getUserProfile();
      if (profileResult is ApiSuccess) {
        final profile = profileResult.data;
        if (profile.containsKey('permissions')) {
          _permissions = List<String>.from(profile['permissions']);
        }
        if (profile.containsKey('groups')) {
          _groups = List<String>.from(profile['groups']);
        }
        if (profile.containsKey('user_id')) {
          _userId = profile['user_id'];
        }
        if (profile.containsKey('username')) {
          _username = profile['username'];
        }
        if (profile.containsKey('employee_id')) {
          _employeeId = profile['employee_id'];
        }
        notifyListeners();
      }
    } catch (e) {
      debugPrint("Error loading permissions: $e");
    }
  }

  void clearPermissions() {
    _permissions = [];
    _groups = [];
    _userId = null;
    _username = null;
    _employeeId = null;
    notifyListeners();
  }
}
