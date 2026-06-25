import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../services/api_result.dart';
import 'employee_form_dialog.dart';
import 'audit_logs_page.dart';
import '../services/websocket_service.dart';
import '../core/di/injection.dart';
import '../data/repositories/employee_repository.dart';
import '../domain/models/employee.dart';
import 'employee_profile_page.dart';

class EmployeesPage extends StatefulWidget {
  const EmployeesPage({super.key});

  @override
  State<EmployeesPage> createState() => _EmployeesPageState();
}

class _EmployeesPageState extends State<EmployeesPage> {
  List<dynamic> _allEmployees = [];
  List<dynamic> _employees = [];
  bool _isLoading = true;
  bool _showDeleted = false;
  
  String _searchQuery = '';
  final TextEditingController _searchController = TextEditingController();
  int _sortColumnIndex = 0;
  bool _isAscending = true;
  final ScrollController _horizontalScrollController = ScrollController();
  final ScrollController _verticalScrollController = ScrollController();
  Timer? _debounce;
  int _currentPage = 1;
  bool _hasMore = true;
  bool _isLoadingMore = false;
  StreamSubscription? _wsSubscription;

  @override
  void initState() {
    super.initState();
    _fetchEmployees();
    _verticalScrollController.addListener(_onScroll);
    _wsSubscription = getIt<WebSocketService>().updates.listen((event) {
      if (event['model'] == 'Employee' || event['model'] == 'Department' || event['model'] == 'Company') {
        _fetchEmployeesSilently();
      }
    });
  }

  Future<void> _fetchEmployeesSilently() async {
    try {
      final response = await getIt<EmployeeRepository>().getEmployees(showDeleted: _showDeleted, page: 1);
      if (response is ApiSuccess) {
        if (mounted) {
          setState(() {
            _currentPage = 1;
            if (response.data is Map && response.data.containsKey('results')) {
              _allEmployees = response.data['results'];
              _hasMore = response.data['next'] != null;
            } else if (response.data is List) {
              _allEmployees = response.data;
              _hasMore = false;
            }
            _applySearchAndSort();
          });
        }
      }
    } catch (e) {
      debugPrint('Error silent fetch: $e');
    }
  }

  void _onScroll() {
    if (_verticalScrollController.position.pixels >= _verticalScrollController.position.maxScrollExtent - 200) {
      if (!_isLoadingMore && _hasMore) {
        _loadMoreEmployees();
      }
    }
  }

  Future<void> _fetchEmployees() async {
    setState(() {
      _isLoading = true;
      _currentPage = 1;
      _hasMore = true;
      _allEmployees.clear();
      _employees.clear();
    });
    try {
      final response = await getIt<EmployeeRepository>().getEmployees(showDeleted: _showDeleted, page: _currentPage);
      if (response is ApiSuccess) {
        setState(() {
          if (response.data is Map && response.data.containsKey('results')) {
            _allEmployees = response.data['results'];
            _hasMore = response.data['next'] != null;
          } else if (response.data is List) {
            _allEmployees = response.data;
            _hasMore = false;
          }
          _applySearchAndSort();
        });
      }
    } catch (e) {
      debugPrint('Error fetching employees: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _loadMoreEmployees() async {
    setState(() => _isLoadingMore = true);
    _currentPage++;
    try {
      final response = await getIt<EmployeeRepository>().getEmployees(showDeleted: _showDeleted, page: _currentPage);
      if (response is ApiSuccess) {
        setState(() {
          if (response.data is Map && response.data.containsKey('results')) {
            _allEmployees.addAll(response.data['results']);
            _hasMore = response.data['next'] != null;
          } else if (response.data is List) {
            _allEmployees.addAll(response.data);
            _hasMore = false;
          }
          _applySearchAndSort();
        });
      }
    } catch (e) {
      debugPrint('Error loading more employees: $e');
    } finally {
      if (mounted) setState(() => _isLoadingMore = false);
    }
  }

  @override
  void dispose() {
    _wsSubscription?.cancel();
    _debounce?.cancel();
    _horizontalScrollController.dispose();
    _verticalScrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 300), () {
      setState(() {
        _searchQuery = query;
        _applySearchAndSort();
      });
    });
  }

  void _clearSearch() {
    _searchController.clear();
    _onSearchChanged('');
  }

  void _sort(int columnIndex, bool ascending) {
    setState(() {
      _sortColumnIndex = columnIndex;
      _isAscending = ascending;
      _applySearchAndSort();
    });
  }

  void _applySearchAndSort() {
    var filtered = _allEmployees.where((emp) {
      final q = _searchQuery.toLowerCase();
      final name = '${emp['first_name'] ?? ''} ${emp['last_name'] ?? ''} ${emp['username'] ?? ''}'.toLowerCase();
      final id = (emp['employee_id']?.toString() ?? '').toLowerCase();
      final phone = (emp['phone']?.toString() ?? '').toLowerCase();
      final dep = (emp['department_name']?.toString() ?? emp['department']?.toString() ?? '').toLowerCase();
      final comp = (emp['company_name']?.toString() ?? emp['company']?.toString() ?? '').toLowerCase();
      final des = (emp['designation']?.toString() ?? '').toLowerCase();
      
      return name.contains(q) || id.contains(q) || phone.contains(q) || dep.contains(q) || comp.contains(q) || des.contains(q);
    }).toList();

    filtered.sort((a, b) {
      Comparable getField(dynamic emp) {
        switch (_sortColumnIndex) {
          case 0: return emp['employee_id']?.toString() ?? '';
          case 1: 
             String n = emp['username'] ?? '';
             if (emp['first_name'] != null && emp['first_name'].isNotEmpty) n = '${emp['first_name']} ${emp['last_name']}';
             return n;
          case 2: return emp['designation']?.toString() ?? '';
          case 3: return emp['company_name'] ?? emp['company']?.toString() ?? '';
          case 4: return emp['department_name']?.toString() ?? '';
          case 5: return emp['phone']?.toString() ?? '';
          case 6: return (emp['is_active'] == true ? 1 : 0).toString();
          default: return '';
        }
      }
      final Comparable aValue = getField(a);
      final Comparable bValue = getField(b);
      return _isAscending ? Comparable.compare(aValue, bValue) : Comparable.compare(bValue, aValue);
    });

    _employees = filtered;
  }

  void _showEmployeeDialog([Map<String, dynamic>? employee]) async {
    final bool? shouldRefresh = await showDialog(
      context: context,
      builder: (ctx) => EmployeeFormDialog(employee: employee),
    );
    if (shouldRefresh == true) {
      _fetchEmployees();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(employee == null ? 'Employee successfully added!' : 'Employee successfully updated!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    }
  }

  void _deleteEmployee(int id) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Employee'),
        content: const Text('Are you sure you want to delete this employee?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Delete', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      setState(() { _isLoading = true; });
      final result = await getIt<EmployeeRepository>().deleteEmployee(id);
      if (result is ApiSuccess) {
        _fetchEmployees();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Employee successfully deleted!'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else if (result is ApiError) {
        final err = result as ApiError;
        if (mounted) {
          setState(() { _isLoading = false; });
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(err.message),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  void _restoreEmployee(int id) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Restore Employee'),
        content: const Text('Are you sure you want to restore this employee?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Restore', style: TextStyle(color: Colors.green)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      setState(() { _isLoading = true; });
      final result = await getIt<EmployeeRepository>().restoreEmployee(id);
      if (result is ApiSuccess) {
        _fetchEmployees();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Employee successfully restored!'), backgroundColor: Colors.green),
          );
        }
      } else if (result is ApiError) {
        final err = result as ApiError;
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(err.message), backgroundColor: Colors.red),
          );
        }
      }
    }
  }

  void _showHistoryDialog(int targetUserId) {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Container(
          width: MediaQuery.of(context).size.width * 0.9,
          height: MediaQuery.of(context).size.height * 0.9,
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Employee History', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(ctx)),
                ],
              ),
              const SizedBox(height: 16),
              Expanded(child: AuditLogsPage(targetUserId: targetUserId)),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : const Color(0xFF1E293B);
    final authProvider = Provider.of<AuthProvider>(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Wrap(
          spacing: 16,
          runSpacing: 16,
          alignment: WrapAlignment.spaceBetween,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            Container(
              constraints: const BoxConstraints(maxWidth: 300),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey.withOpacity(0.2)),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: TextField(
                controller: _searchController,
                onChanged: _onSearchChanged,
                style: TextStyle(color: textColor),
                decoration: InputDecoration(
                  icon: const Icon(Icons.search, color: Colors.grey),
                  hintText: 'Search employees...',
                  border: InputBorder.none,
                  suffixIcon: _searchQuery.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear, color: Colors.grey),
                          onPressed: _clearSearch,
                        )
                      : null,
                ),
              ),
            ),
            Wrap(
              spacing: 16,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('Show Deleted', style: TextStyle(fontWeight: FontWeight.bold)),
                    Switch(
                      value: _showDeleted,
                      onChanged: (val) {
                        setState(() {
                          _showDeleted = val;
                          _fetchEmployees();
                        });
                      },
                    ),
                  ],
                ),
                if (authProvider.canAddEmployee() && !_showDeleted)
                  ElevatedButton.icon(
                    onPressed: () => _showEmployeeDialog(),
                    icon: const Icon(Icons.add),
                    label: const Text('Add Employee'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Theme.of(context).colorScheme.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 24),
        Expanded(
          child: Card(
            elevation: 0,
            clipBehavior: Clip.antiAlias,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            color: Theme.of(context).cardColor,
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _employees.isEmpty
                    ? Center(child: Text('No employees found.', style: TextStyle(color: textColor)))
                    : LayoutBuilder(
                        builder: (context, constraints) {
                          if (constraints.maxWidth < 800) {
                            return ListView.builder(
                              controller: _verticalScrollController,
                              itemCount: _employees.length + (_isLoadingMore ? 1 : 0),
                              itemBuilder: (context, index) {
                                if (index == _employees.length) {
                                  return const Padding(
                                    padding: EdgeInsets.all(16.0),
                                    child: Center(child: CircularProgressIndicator()),
                                  );
                                }
                                final emp = _employees[index];
                                String name = emp['username'] ?? 'User ID: ${emp['user']}';
                                if (emp['first_name'] != null && emp['first_name'].isNotEmpty) {
                                  name = '${emp['first_name']} ${emp['last_name']}';
                                }
                                return Card(
                                  margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                  child: ListTile(
                                    onTap: () {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (context) => EmployeeProfilePage(
                                            employeeId: emp['id'],
                                            employeeName: name,
                                            employee: Employee.fromJson(Map<String, dynamic>.from(emp)),
                                          ),
                                        ),
                                      );
                                    },
                                    leading: CircleAvatar(
                                      backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
                                      child: Text(
                                        name.isNotEmpty ? name[0].toUpperCase() : '?',
                                        style: TextStyle(color: Theme.of(context).primaryColor, fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                    title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
                                    subtitle: Text(emp['designation']?.toString() ?? 'N/A'),
                                    trailing: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        if (authProvider.isManagerOrDeveloper && emp['user'] != null)
                                          IconButton(
                                            icon: const Icon(Icons.history, color: Colors.purple, size: 20),
                                            onPressed: () => _showHistoryDialog(emp['user']),
                                          ),
                                        if (_showDeleted) ...[
                                          if (authProvider.canDeleteEmployee())
                                            IconButton(
                                              icon: const Icon(Icons.restore, color: Colors.green, size: 20),
                                              onPressed: () => _restoreEmployee(emp['id']),
                                            ),
                                        ] else ...[
                                          if (authProvider.canEditEmployee())
                                            IconButton(
                                              icon: const Icon(Icons.edit, color: Colors.blue, size: 20),
                                              onPressed: () => _showEmployeeDialog(emp),
                                            ),
                                        ]
                                      ],
                                    ),
                                  ),
                                );
                              },
                            );
                          }

                          return SingleChildScrollView(
                            scrollDirection: Axis.vertical,
                            controller: _verticalScrollController,
                            child: Scrollbar(
                              controller: _horizontalScrollController,
                              thumbVisibility: true,
                              child: SingleChildScrollView(
                                controller: _horizontalScrollController,
                                scrollDirection: Axis.horizontal,
                                child: ConstrainedBox(
                                  constraints: const BoxConstraints(minWidth: 1000), 
                                  child: Column(
                                    children: [
                                      DataTable(
                                        showCheckboxColumn: false,
                                        sortColumnIndex: _sortColumnIndex,
                                        sortAscending: _isAscending,
                                        headingRowColor: WidgetStateProperty.resolveWith((states) => Theme.of(context).cardColor.withOpacity(0.8)),
                                        columns: [
                                          DataColumn(label: const Text('ID', style: TextStyle(fontWeight: FontWeight.bold)), onSort: _sort),
                                          DataColumn(label: const Text('Name', style: TextStyle(fontWeight: FontWeight.bold)), onSort: _sort),
                                          DataColumn(label: const Text('Designation', style: TextStyle(fontWeight: FontWeight.bold)), onSort: _sort),
                                          DataColumn(label: const Text('Company', style: TextStyle(fontWeight: FontWeight.bold)), onSort: _sort),
                                          DataColumn(label: const Text('Department', style: TextStyle(fontWeight: FontWeight.bold)), onSort: _sort),
                                          DataColumn(label: const Text('Phone', style: TextStyle(fontWeight: FontWeight.bold)), onSort: _sort),
                                          DataColumn(label: const Text('Status', style: TextStyle(fontWeight: FontWeight.bold)), onSort: _sort),
                                          const DataColumn(label: Text('Actions', style: TextStyle(fontWeight: FontWeight.bold))),
                                        ],
                                        rows: _employees.map((emp) {
                                          String name = emp['username'] ?? 'User ID: ${emp['user']}';
                                          if (emp['first_name'] != null && emp['first_name'].isNotEmpty) {
                                            name = '${emp['first_name']} ${emp['last_name']}';
                                          }

                                          return DataRow(
                                            onSelectChanged: (_) {
                                              Navigator.push(
                                                context,
                                                MaterialPageRoute(
                                                  builder: (context) => EmployeeProfilePage(
                                                    employeeId: emp['id'],
                                                    employeeName: name,
                                                    employee: Employee.fromJson(Map<String, dynamic>.from(emp)),
                                                  ),
                                                ),
                                              );
                                            },
                                            cells: [
                                              DataCell(Text(emp['employee_id']?.toString() ?? 'N/A')),
                                              DataCell(Text(name)),
                                              DataCell(Text(emp['designation']?.toString() ?? 'N/A')),
                                              DataCell(Text(emp['company_name'] ?? emp['company']?.toString() ?? 'N/A')),
                                              DataCell(Text(emp['department_name'] ?? emp['department']?.toString() ?? 'N/A')),
                                              DataCell(Text(emp['phone']?.toString() ?? 'N/A')),
                                              DataCell(
                                                Container(
                                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                                  decoration: BoxDecoration(
                                                    color: _showDeleted ? Colors.grey.withOpacity(0.1) : ((emp['is_active'] ?? true) ? Colors.green.withOpacity(0.1) : Colors.red.withOpacity(0.1)),
                                                    borderRadius: BorderRadius.circular(12),
                                                  ),
                                                  child: Text(
                                                    _showDeleted ? 'Deleted' : ((emp['is_active'] ?? true) ? 'Active' : 'Inactive'),
                                                    style: TextStyle(
                                                      color: _showDeleted ? Colors.grey : ((emp['is_active'] ?? true) ? Colors.green : Colors.red),
                                                      fontWeight: FontWeight.bold,
                                                    ),
                                                  ),
                                                ),
                                              ),
                                              DataCell(Row(
                                                mainAxisSize: MainAxisSize.min,
                                                children: [
                                                  if (authProvider.isManagerOrDeveloper && emp['user'] != null)
                                                    IconButton(
                                                      icon: const Icon(Icons.history, color: Colors.purple),
                                                      onPressed: () => _showHistoryDialog(emp['user']),
                                                      tooltip: 'View History',
                                                    ),
                                                  if (_showDeleted) ...[
                                                    if (authProvider.canDeleteEmployee())
                                                      IconButton(
                                                        icon: const Icon(Icons.restore, color: Colors.green),
                                                        onPressed: () => _restoreEmployee(emp['id']),
                                                        tooltip: 'Restore Employee',
                                                      ),
                                                  ] else ...[
                                                    if (authProvider.canEditEmployee())
                                                      IconButton(
                                                        icon: const Icon(Icons.edit, color: Colors.blue),
                                                        onPressed: () => _showEmployeeDialog(emp),
                                                        tooltip: 'Edit',
                                                      ),
                                                    if (authProvider.canDeleteEmployee() && emp['user'] != authProvider.userId)
                                                      IconButton(
                                                        icon: const Icon(Icons.delete, color: Colors.red),
                                                        onPressed: () => _deleteEmployee(emp['id']),
                                                        tooltip: 'Delete',
                                                      ),
                                                  ]
                                                ],
                                              )),
                                            ]
                                          );
                                        }).toList(),
                                      ),
                                      if (_isLoadingMore)
                                        const Padding(
                                          padding: EdgeInsets.all(16.0),
                                          child: CircularProgressIndicator(),
                                        ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ),
      ],
    );
  }
}
