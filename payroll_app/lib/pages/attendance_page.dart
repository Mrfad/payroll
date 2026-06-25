import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/api_result.dart';
import '../domain/models/employee.dart';
import 'employee_profile_page.dart';

class AttendancePage extends StatefulWidget {
  const AttendancePage({super.key});

  @override
  State<AttendancePage> createState() => _AttendancePageState();
}

class _AttendancePageState extends State<AttendancePage> {
  bool _isLoading = true;
  bool _isHR = false;
  int? _myEmployeeId;
  String _myEmployeeName = '';
  List<Employee> _employees = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _initDashboard();
  }

  Future<void> _initDashboard() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      // 1. Get user profile to check roles
      final profileResult = await ApiService.getUserProfile();
      if (profileResult is ApiSuccess) {
        final groups = profileResult.data['groups'] as List;
        _isHR = groups.contains('Managers') || profileResult.data['permissions'].contains('is_staff') == true;
        _myEmployeeId = profileResult.data['employee_id'];
        _myEmployeeName = profileResult.data['first_name'] ?? profileResult.data['username'] ?? 'Me';

        // 2. If HR, fetch employees list
        if (_isHR) {
          final empResult = await ApiService.getEmployees();
          if (empResult is ApiSuccess) {
            final data = empResult.data['results'] as List;
            _employees = data.map((json) => Employee.fromJson(json)).toList();
          } else {
            throw Exception((empResult as ApiError).message);
          }
        }
      } else {
        throw Exception((profileResult as ApiError).message);
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      if (mounted) setState(() { _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 48),
            const SizedBox(height: 16),
            Text('Error: $_error'),
            ElevatedButton(onPressed: _initDashboard, child: const Text('Retry'))
          ],
        ),
      );
    }

    // If NOT HR, show their own attendance directly!
    if (!_isHR) {
      if (_myEmployeeId == null) {
        return const Center(child: Text('No employee profile linked to your account.'));
      }
      return EmployeeProfilePage(employeeId: _myEmployeeId!, employeeName: _myEmployeeName);
    }

    // If HR, show the Enterprise HR Dashboard (List of Employees)
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : const Color(0xFF1E293B);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                'HR Attendance Dashboard', 
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: textColor),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _initDashboard,
              tooltip: 'Refresh',
            ),
          ],
        ),
        const SizedBox(height: 16),
        Text('Select an employee to view their detailed attendance records.', style: TextStyle(color: Colors.grey[600])),
        const SizedBox(height: 24),
        Expanded(
          child: _employees.isEmpty
              ? const Center(child: Text('No active employees found.'))
              : ListView.builder(
                  itemCount: _employees.length,
                  itemBuilder: (context, index) {
                    final emp = _employees[index];
                    return Card(
                      elevation: 1,
                      margin: const EdgeInsets.only(bottom: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
                          child: Text(
                            emp.firstName.isNotEmpty ? emp.firstName[0] : emp.username[0].toUpperCase(),
                            style: TextStyle(color: Theme.of(context).primaryColor, fontWeight: FontWeight.bold),
                          ),
                        ),
                        title: Text('${emp.firstName} ${emp.lastName}'.trim().isEmpty ? emp.username : '${emp.firstName} ${emp.lastName}'),
                        subtitle: Text('${emp.employeeId} • ${emp.designation ?? 'No Designation'}'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () {
                          // Navigate to detailed view
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => EmployeeProfilePage(
                                employeeId: emp.id,
                                employeeName: '${emp.firstName} ${emp.lastName}'.trim().isEmpty ? emp.username : '${emp.firstName} ${emp.lastName}',
                                employee: emp,
                              ),
                            ),
                          );
                        },
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }
}
