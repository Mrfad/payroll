import 'dart:convert';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../core/database/database_helper.dart';
import '../core/di/injection.dart';
import '../data/repositories/employee_repository.dart';
import 'api_result.dart';
import 'package:flutter/foundation.dart';

class SyncService {
  static final SyncService _instance = SyncService._internal();
  factory SyncService() => _instance;
  SyncService._internal();

  final _dbHelper = DatabaseHelper();
  bool _isSyncing = false;

  void initialize() {
    Connectivity().onConnectivityChanged.listen((List<ConnectivityResult> results) {
      // If we have internet, try to sync
      if (!results.contains(ConnectivityResult.none)) {
        syncOfflineMutations();
      }
    });
  }

  Future<void> syncOfflineMutations() async {
    if (_isSyncing) return;
    _isSyncing = true;
    
    try {
      final db = await _dbHelper.database;
      final mutations = await db.query('offline_mutations', orderBy: 'id ASC');
      
      for (var mutation in mutations) {
        final id = mutation['id'] as int;
        final endpoint = mutation['endpoint'] as String;
        final method = mutation['method'] as String;
        final payloadStr = mutation['payload'] as String;
        
        final payload = payloadStr.isNotEmpty && payloadStr != '{}' 
            ? jsonDecode(payloadStr) as Map<String, dynamic> 
            : null;
            
        try {
          ApiResult? apiResult;
          if (method == 'POST') {
             apiResult = await getIt<EmployeeRepository>().enrollEmployee(payload ?? {});
          } else if (method == 'PATCH') {
             final parts = endpoint.split('/');
             final empIdStr = parts[parts.length - 2];
             final empId = int.tryParse(empIdStr);
             if (empId != null) {
                apiResult = await getIt<EmployeeRepository>().updateEmployee(empId, payload ?? {});
             }
          } else if (method == 'DELETE') {
             final parts = endpoint.split('/');
             final empIdStr = parts[parts.length - 2];
             final empId = int.tryParse(empIdStr);
             if (empId != null) {
                apiResult = await getIt<EmployeeRepository>().deleteEmployee(empId);
             }
          }
          
          if (apiResult is ApiError) {
             throw Exception(apiResult.message);
          }
          
          // If successful (or throws 404 which means already deleted etc), delete from queue
          await db.delete('offline_mutations', where: 'id = ?', whereArgs: [id]);
        } catch (e) {
          debugPrint('Failed to sync mutation $id: $e');
          // We will retry on next connection
          break; 
        }
      }
    } finally {
      _isSyncing = false;
    }
  }
}
