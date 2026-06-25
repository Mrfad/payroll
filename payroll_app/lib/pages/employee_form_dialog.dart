import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../services/api_result.dart';
import '../services/websocket_service.dart';
import '../core/di/injection.dart';
import '../data/repositories/reference_repository.dart';
import '../data/repositories/employee_repository.dart';
import 'dart:async';

class EmployeeFormDialog extends StatefulWidget {
  final Map<String, dynamic>? employee;

  const EmployeeFormDialog({super.key, this.employee});

  @override
  State<EmployeeFormDialog> createState() => _EmployeeFormDialogState();
}

class _EmployeeFormDialogState extends State<EmployeeFormDialog> {
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  bool _isFetchingRefs = true;
  StreamSubscription? _wsSubscription;

  List<dynamic> _companies = [];
  List<dynamic> _departments = [];

  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  
  int? _selectedCompanyId;
  int? _selectedDepartmentId;
  
  final _employeeIdController = TextEditingController();
  final _designationController = TextEditingController();
  final _phoneController = TextEditingController();
  final _baseSalaryController = TextEditingController();

  bool _isActive = true;
  String? _companyError;

  @override
  void initState() {
    super.initState();
    _fetchRefs();
    if (widget.employee != null) {
      final emp = widget.employee!;
      _selectedCompanyId = emp['company'];
      _selectedDepartmentId = emp['department'];
      _employeeIdController.text = emp['employee_id']?.toString() ?? '';
      _designationController.text = emp['designation']?.toString() ?? '';
      _phoneController.text = emp['phone']?.toString() ?? '';
      _baseSalaryController.text = emp['base_salary']?.toString() ?? '';
      _isActive = emp['is_active'] ?? true;
    } else {
      _employeeIdController.text = 'Auto-generated';
    }

    _wsSubscription = getIt<WebSocketService>().updates.listen((event) {
      if (event['model'] == 'Company' || event['model'] == 'Department') {
        _fetchRefsSilently();
      }
    });
  }

  Future<void> _fetchRefsSilently() async {
    try {
      final comps = await getIt<ReferenceRepository>().getCompanies();
      final depts = await getIt<ReferenceRepository>().getDepartments();
      if (mounted) {
        setState(() {
          if (comps is ApiSuccess) _companies = comps.data is Map ? comps.data['results'] : comps.data;
          if (depts is ApiSuccess) {
            _departments = depts.data is Map ? depts.data['results'] : depts.data;
            if (_selectedDepartmentId != null) {
              final exists = _departments.any((d) => d['id'] == _selectedDepartmentId);
              if (!exists) _selectedDepartmentId = null;
            }
          }
        });
      }
    } catch (e) {
      debugPrint("Error fetching refs silently: $e");
    }
  }

  Future<void> _fetchRefs() async {
    try {
      final comps = await getIt<ReferenceRepository>().getCompanies();
      final depts = await getIt<ReferenceRepository>().getDepartments();
      if (mounted) {
        setState(() {
          if (comps is ApiSuccess) _companies = comps.data is Map ? comps.data['results'] : comps.data;
          if (depts is ApiSuccess) _departments = depts.data is Map ? depts.data['results'] : depts.data;
          _isFetchingRefs = false;
        });
      }
    } catch (e) {
      debugPrint("Error fetching refs: $e");
      if (mounted) setState(() => _isFetchingRefs = false);
    }
  }

  void _submit() async {
    bool hasDropdownError = false;
    setState(() {
      if (_selectedCompanyId == null) {
        _companyError = 'Required';
        hasDropdownError = true;
      } else {
        _companyError = null;
      }
    });

    if (_formKey.currentState!.validate() && !hasDropdownError) {
      setState(() => _isLoading = true);

      Map<String, dynamic> data = {
        'company': _selectedCompanyId,
        'department': _selectedDepartmentId,
        'designation': _designationController.text,
        'phone': _phoneController.text,
        'is_active': _isActive,
      };
      
      if (_baseSalaryController.text.isNotEmpty) {
        data['base_salary'] = _baseSalaryController.text;
      }

      try {
        ApiResult<dynamic> result;
        if (widget.employee == null) {
          // Creating via enroll
          data['username'] = _usernameController.text;
          data['email'] = _emailController.text;
          data['password'] = _passwordController.text;
          data['first_name'] = _firstNameController.text;
          data['last_name'] = _lastNameController.text;

          result = await getIt<EmployeeRepository>().enrollEmployee(data);
        } else {
          result = await getIt<EmployeeRepository>().updateEmployee(widget.employee!['id'], data);
        }

        if (result is ApiSuccess) {
          Navigator.pop(context, true);
        } else if (result is ApiError) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result.message), backgroundColor: Colors.red));
        }
      } catch (e) {
        debugPrint('Error saving employee: $e');
      } finally {
        if (mounted) setState(() => _isLoading = false);
      }
    }
  }

  @override
  void dispose() {
    _wsSubscription?.cancel();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _employeeIdController.dispose();
    _designationController.dispose();
    _baseSalaryController.dispose();
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isEditing = widget.employee != null;

    return AlertDialog(
      title: Text(isEditing ? 'Edit Employee' : 'Add Employee'),
      content: SizedBox(
        width: 500,
        child: _isFetchingRefs
            ? const SizedBox(height: 100, child: Center(child: CircularProgressIndicator()))
            : SingleChildScrollView(
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (!isEditing) ...[
                        Text('User Details', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(child: TextFormField(
                              controller: _usernameController,
                              decoration: const InputDecoration(labelText: 'Username', border: OutlineInputBorder()),
                              validator: (val) => val!.isEmpty ? 'Required' : null,
                            )),
                            const SizedBox(width: 12),
                            Expanded(child: TextFormField(
                              controller: _emailController,
                              decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
                              validator: (val) => val!.isEmpty ? 'Required' : null,
                            )),
                          ],
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _passwordController,
                          obscureText: true,
                          decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
                          validator: (val) => val!.isEmpty ? 'Required' : null,
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(child: TextFormField(
                              controller: _firstNameController,
                              decoration: const InputDecoration(labelText: 'First Name', border: OutlineInputBorder()),
                            )),
                            const SizedBox(width: 12),
                            Expanded(child: TextFormField(
                              controller: _lastNameController,
                              decoration: const InputDecoration(labelText: 'Last Name', border: OutlineInputBorder()),
                            )),
                          ],
                        ),
                        const SizedBox(height: 16),
                        const Divider(),
                        const SizedBox(height: 16),
                      ],
                      Text('Employment Details', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: Focus(
                              onKeyEvent: (node, event) {
                                if (event is KeyDownEvent) {
                                  if (event.logicalKey == LogicalKeyboardKey.arrowDown) {
                                    if (_companies.isNotEmpty) {
                                      int idx = _companies.indexWhere((c) => c['id'] == _selectedCompanyId);
                                      if (idx < _companies.length - 1) {
                                        setState(() {
                                          _selectedCompanyId = _companies[idx + 1]['id'];
                                          _selectedDepartmentId = null;
                                          _companyError = null;
                                        });
                                      } else if (idx == -1) {
                                        setState(() {
                                          _selectedCompanyId = _companies[0]['id'];
                                          _selectedDepartmentId = null;
                                          _companyError = null;
                                        });
                                      }
                                    }
                                    return KeyEventResult.handled;
                                  } else if (event.logicalKey == LogicalKeyboardKey.arrowUp) {
                                    if (_companies.isNotEmpty) {
                                      int idx = _companies.indexWhere((c) => c['id'] == _selectedCompanyId);
                                      if (idx > 0) {
                                        setState(() {
                                          _selectedCompanyId = _companies[idx - 1]['id'];
                                          _selectedDepartmentId = null;
                                          _companyError = null;
                                        });
                                      }
                                    }
                                    return KeyEventResult.handled;
                                  }
                                }
                                return KeyEventResult.ignored;
                              },
                              child: DropdownButtonFormField<int>(
                                isExpanded: true,
                                decoration: InputDecoration(
                                  labelText: 'Company',
                                  border: const OutlineInputBorder(),
                                  errorText: _companyError,
                                ),
                                value: _selectedCompanyId,
                                items: _companies.map<DropdownMenuItem<int>>((comp) {
                                  return DropdownMenuItem<int>(
                                    value: comp['id'],
                                    child: Text(comp['name']),
                                  );
                                }).toList(),
                                onChanged: (val) => setState(() {
                                  if (_selectedCompanyId != val) {
                                    _selectedCompanyId = val;
                                    _selectedDepartmentId = null;
                                    _companyError = null;
                                  }
                                }),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Focus(
                              onKeyEvent: (node, event) {
                                if (event is KeyDownEvent) {
                                  final depts = _departments.where((d) => d['company'].toString() == _selectedCompanyId.toString()).toList();
                                  if (event.logicalKey == LogicalKeyboardKey.arrowDown) {
                                    if (depts.isNotEmpty) {
                                      int idx = depts.indexWhere((d) => d['id'] == _selectedDepartmentId);
                                      if (idx < depts.length - 1) {
                                        setState(() => _selectedDepartmentId = depts[idx + 1]['id']);
                                      } else if (idx == -1) {
                                        setState(() => _selectedDepartmentId = depts[0]['id']);
                                      }
                                    }
                                    return KeyEventResult.handled;
                                  } else if (event.logicalKey == LogicalKeyboardKey.arrowUp) {
                                    if (depts.isNotEmpty) {
                                      int idx = depts.indexWhere((d) => d['id'] == _selectedDepartmentId);
                                      if (idx > 0) {
                                        setState(() => _selectedDepartmentId = depts[idx - 1]['id']);
                                      }
                                    }
                                    return KeyEventResult.handled;
                                  }
                                }
                                return KeyEventResult.ignored;
                              },
                              child: DropdownButtonFormField<int>(
                                isExpanded: true,
                                decoration: const InputDecoration(labelText: 'Department (Optional)', border: OutlineInputBorder()),
                                value: _selectedDepartmentId,
                                items: _departments.where((d) => d['company'].toString() == _selectedCompanyId.toString()).map<DropdownMenuItem<int>>((dept) {
                                  return DropdownMenuItem<int>(
                                    value: dept['id'],
                                    child: Text(dept['name']),
                                  );
                                }).toList(),
                                onChanged: (val) => setState(() => _selectedDepartmentId = val),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(child: TextFormField(
                            controller: _employeeIdController,
                            readOnly: true,
                            decoration: InputDecoration(
                              labelText: isEditing ? 'Employee ID' : 'Employee ID (Auto-generated)', 
                              border: const OutlineInputBorder(),
                              filled: true,
                              fillColor: Theme.of(context).disabledColor.withOpacity(0.1),
                            ),
                          )),
                          const SizedBox(width: 12),
                          Expanded(child: TextFormField(
                            controller: _designationController,
                            decoration: const InputDecoration(labelText: 'Designation', border: OutlineInputBorder()),
                          )),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(child: TextFormField(
                            controller: _phoneController,
                            decoration: const InputDecoration(labelText: 'Phone', border: OutlineInputBorder()),
                          )),
                          const SizedBox(width: 12),
                          Expanded(child: TextFormField(
                            controller: _baseSalaryController,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(labelText: 'Base Salary', border: OutlineInputBorder()),
                          )),
                        ],
                      ),
                      if (widget.employee == null || widget.employee!['user'] != Provider.of<AuthProvider>(context, listen: false).userId) ...[
                        const SizedBox(height: 16),
                        SwitchListTile(
                          title: const Text('Account Active'),
                          subtitle: const Text('If disabled, the user cannot log in, but their data remains.'),
                          value: _isActive,
                          onChanged: (val) => setState(() => _isActive = val),
                          contentPadding: EdgeInsets.zero,
                        ),
                      ],
                    ],
                  ),
                ),
              ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: (_isLoading || _isFetchingRefs) ? null : _submit,
          style: ElevatedButton.styleFrom(
            backgroundColor: Theme.of(context).colorScheme.primary,
            foregroundColor: Colors.white,
          ),
          child: _isLoading ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Text('Save'),
        ),
      ],
    );
  }
}
