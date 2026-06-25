import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'dart:async';
import '../domain/models/employee.dart';
import '../domain/models/attendance_record.dart';
import '../domain/models/payroll_entry.dart';
import '../services/api_service.dart';
import '../services/api_result.dart';
import '../services/websocket_service.dart';
import '../core/di/injection.dart';

class EmployeeProfilePage extends StatefulWidget {
  final int employeeId;
  final String employeeName;
  final Employee? employee;

  const EmployeeProfilePage({
    super.key,
    required this.employeeId,
    required this.employeeName,
    this.employee,
  });

  @override
  State<EmployeeProfilePage> createState() => _EmployeeProfilePageState();
}

class _EmployeeProfilePageState extends State<EmployeeProfilePage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  // Attendance state
  bool _isLoadingAttendance = true;
  List<AttendanceRecord> _attendanceRecords = [];
  String? _attendanceError;

  // Payslips state
  bool _isLoadingPayslips = true;
  List<PayrollEntry> _payslips = [];
  String? _payslipsError;

  StreamSubscription? _wsSubscription;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetchAttendance();
    _fetchPayslips();
    
    _wsSubscription = getIt<WebSocketService>().updates.listen((update) {
      if (!mounted) return;
      if (update['model'] == 'AttendanceRecord') {
        _fetchAttendanceSilently();
      } else if (update['model'] == 'PayrollEntry') {
        _fetchPayslipsSilently();
      }
    });
  }

  @override
  void dispose() {
    _wsSubscription?.cancel();
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchAttendance() async {
    setState(() { _isLoadingAttendance = true; _attendanceError = null; });
    try {
      final result = await ApiService.getAttendanceRecords(employeeId: widget.employeeId);
      if (result is ApiSuccess) {
        final data = result.data['results'] as List;
        _attendanceRecords = data.map((json) => AttendanceRecord.fromJson(json)).toList();
      } else {
        throw Exception((result as ApiError).message);
      }
    } catch (e) {
      _attendanceError = e.toString();
    } finally {
      if (mounted) setState(() { _isLoadingAttendance = false; });
    }
  }

  Future<void> _fetchPayslips() async {
    setState(() { _isLoadingPayslips = true; _payslipsError = null; });
    try {
      final result = await ApiService.getPayrollEntries(employeeId: widget.employeeId);
      if (result is ApiSuccess) {
        final data = result.data['results'] as List;
        _payslips = data.map((json) => PayrollEntry.fromJson(json)).toList();
      } else {
        throw Exception((result as ApiError).message);
      }
    } catch (e) {
      _payslipsError = e.toString();
    } finally {
      if (mounted) setState(() { _isLoadingPayslips = false; });
    }
  }

  Future<void> _fetchAttendanceSilently() async {
    try {
      final result = await ApiService.getAttendanceRecords(employeeId: widget.employeeId);
      if (result is ApiSuccess) {
        final data = result.data['results'] as List;
        if (mounted) {
          setState(() {
            _attendanceRecords = data.map((json) => AttendanceRecord.fromJson(json)).toList();
          });
        }
      }
    } catch (e) {
      // Ignore silent errors
    }
  }

  Future<void> _fetchPayslipsSilently() async {
    try {
      final result = await ApiService.getPayrollEntries(employeeId: widget.employeeId);
      if (result is ApiSuccess) {
        final data = result.data['results'] as List;
        if (mounted) {
          setState(() {
            _payslips = data.map((json) => PayrollEntry.fromJson(json)).toList();
          });
        }
      }
    } catch (e) {
      // Ignore silent errors
    }
  }

  Future<void> _punch(BuildContext context) async {
    final scaffoldMessenger = ScaffoldMessenger.of(context);
    final result = await ApiService.punchEmployee(widget.employeeId);
    if (result is ApiSuccess) {
      scaffoldMessenger.showSnackBar(
        const SnackBar(content: Text('Punch recorded successfully!'), backgroundColor: Colors.green),
      );
    } else {
      scaffoldMessenger.showSnackBar(
        SnackBar(content: Text('Failed to punch: ${(result as ApiError).message}'), backgroundColor: Colors.red),
      );
    }
  }

  String _formatDateTime(String? isoString) {
    if (isoString == null) return '--:--';
    final date = DateTime.parse(isoString).toLocal();
    return DateFormat('hh:mm a').format(date);
  }

  String _formatDuration(int totalSeconds) {
    final hours = totalSeconds ~/ 3600;
    final minutes = (totalSeconds % 3600) ~/ 60;
    if (hours == 0 && minutes == 0) return '0h';
    if (hours == 0) return '${minutes}m';
    return '${hours}h ${minutes}m';
  }

  Widget _buildStatusBadge(String status) {
    Color bgColor;
    Color textColor;
    String label;

    switch (status) {
      case 'present':
        bgColor = Colors.green.withOpacity(0.15);
        textColor = Colors.green[700]!;
        label = 'Present';
        break;
      case 'half_day':
        bgColor = Colors.orange.withOpacity(0.15);
        textColor = Colors.orange[800]!;
        label = 'Half Day';
        break;
      case 'absent':
        bgColor = Colors.red.withOpacity(0.15);
        textColor = Colors.red[700]!;
        label = 'Absent';
        break;
      case 'missing_punch':
        bgColor = Colors.orange.withOpacity(0.2);
        textColor = Colors.orange[900]!;
        label = 'Missing Punch';
        break;
      default:
        bgColor = Colors.grey.withOpacity(0.15);
        textColor = Colors.grey[700]!;
        label = status.toUpperCase();
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: TextStyle(color: textColor, fontWeight: FontWeight.w600, fontSize: 12),
      ),
    );
  }

  Widget _buildMetric(String label, String value, MaterialColor color) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: color[700])),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(color: Colors.grey)),
      ],
    );
  }

  Widget _buildAttendanceTab() {
    if (_isLoadingAttendance) return const Center(child: CircularProgressIndicator());
    if (_attendanceError != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, color: Colors.red[400], size: 48),
            const SizedBox(height: 16),
            const Text('Error loading attendance', style: TextStyle(fontSize: 18)),
            Text(_attendanceError!, style: const TextStyle(color: Colors.grey)),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _fetchAttendance, child: const Text('Try Again'))
          ],
        ),
      );
    }
    if (_attendanceRecords.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.event_busy, color: Colors.grey[400], size: 64),
            const SizedBox(height: 16),
            const Text('No attendance records found', style: TextStyle(fontSize: 18)),
          ],
        ),
      );
    }

    int totalWorkSecs = 0;
    int totalOTSecs = 0;
    int absences = 0;
    for (var r in _attendanceRecords) {
        totalWorkSecs += r.totalWorkSeconds;
        totalOTSecs += r.overtimeSeconds;
        if (r.status == 'absent') absences++;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildMetric('Total Hours', _formatDuration(totalWorkSecs), Colors.blue),
                  _buildMetric('Total OT', _formatDuration(totalOTSecs), Colors.orange),
                  _buildMetric('Absences', '$absences days', Colors.red),
                ],
              ),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('History', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              ElevatedButton.icon(
                onPressed: () => _punch(context),
                icon: const Icon(Icons.fingerprint),
                label: const Text('Punch'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Theme.of(context).primaryColor,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16.0),
            itemCount: _attendanceRecords.length,
            itemBuilder: (context, index) {
              final record = _attendanceRecords[index];
              final dateObj = DateTime.tryParse(record.date);
              final dateStr = dateObj != null ? DateFormat('EEEE, MMM d, yyyy').format(dateObj) : record.date;
              
              return Card(
                elevation: 1,
                margin: const EdgeInsets.only(bottom: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  title: Text(dateStr, style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.arrow_downward, size: 16, color: Colors.green),
                            const SizedBox(width: 4),
                            Text('In: ${_formatDateTime(record.firstIn)}'),
                            const SizedBox(width: 16),
                            const Icon(Icons.arrow_upward, size: 16, color: Colors.orange),
                            const SizedBox(width: 4),
                            Text('Out: ${_formatDateTime(record.lastOut)}'),
                          ],
                        ),
                        if (record.punchedFrom != null && record.punchedFrom!.isNotEmpty) ...[
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              Icon(Icons.device_hub, size: 14, color: Colors.grey[600]),
                              const SizedBox(width: 4),
                              Text(
                                'Source: ${record.punchedFrom}',
                                style: TextStyle(fontSize: 12, color: Colors.grey[700]),
                              ),
                            ],
                          ),
                        ],
                        if (record.isAnomaly && record.anomalyReason != null) ...[
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              const Icon(Icons.warning_amber_rounded, size: 14, color: Colors.red),
                              const SizedBox(width: 4),
                              Expanded(
                                child: Text(
                                  record.anomalyReason!,
                                  style: const TextStyle(fontSize: 12, color: Colors.red, fontStyle: FontStyle.italic),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ],
                    ),
                  ),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    mainAxisSize: MainAxisSize.min, // Fixes the 1px bottom overflow
                    children: [
                      _buildStatusBadge(record.status),
                      const SizedBox(height: 0),
                      Text(_formatDuration(record.totalWorkSeconds), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildPayslipsTab() {
    if (_isLoadingPayslips) return const Center(child: CircularProgressIndicator());
    if (_payslipsError != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, color: Colors.red[400], size: 48),
            const SizedBox(height: 16),
            const Text('Error loading payslips', style: TextStyle(fontSize: 18)),
            Text(_payslipsError!, style: const TextStyle(color: Colors.grey)),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _fetchPayslips, child: const Text('Try Again'))
          ],
        ),
      );
    }
    if (_payslips.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.receipt_long, color: Colors.grey[400], size: 64),
            const SizedBox(height: 16),
            const Text('No payslips available', style: TextStyle(fontSize: 18)),
          ],
        ),
      );
    }

    final currencyFormatter = NumberFormat.currency(symbol: '\$');

    return ListView.builder(
      padding: const EdgeInsets.all(16.0),
      itemCount: _payslips.length,
      itemBuilder: (context, index) {
        final entry = _payslips[index];
        return Card(
          elevation: 1,
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => _showPayslipDetails(entry),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Theme.of(context).primaryColor.withOpacity(0.1),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(Icons.account_balance_wallet, color: Theme.of(context).primaryColor),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Salary / Month', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                              const SizedBox(height: 4),
                              Text(
                                '${entry.periodStart} - ${entry.periodEnd}', 
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(currencyFormatter.format(entry.netPay), style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green[700])),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          const Text('View details', style: TextStyle(fontSize: 12, color: Colors.blue)),
                          const SizedBox(width: 4),
                          const Icon(Icons.chevron_right, size: 14, color: Colors.blue),
                        ],
                      )
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  void _showPayslipDetails(PayrollEntry entry) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        final currencyFormatter = NumberFormat.currency(symbol: '\$');
        final isDark = Theme.of(context).brightness == Brightness.dark;
        
        return Container(
          height: MediaQuery.of(context).size.height * 0.85,
          decoration: BoxDecoration(
            color: isDark ? const Color(0xFF1E293B) : Colors.white,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: Column(
            children: [
              Container(
                margin: const EdgeInsets.symmetric(vertical: 12),
                width: 40,
                height: 4,
                decoration: BoxDecoration(color: Colors.grey[400], borderRadius: BorderRadius.circular(2)),
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text('PAYSLIP', textAlign: TextAlign.center, style: TextStyle(fontSize: 16, letterSpacing: 2, fontWeight: FontWeight.bold, color: Colors.grey)),
                      const SizedBox(height: 8),
                      Text('${entry.periodStart} to ${entry.periodEnd}', textAlign: TextAlign.center, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 24),
                      // EARNINGS
                      const Text('EARNINGS', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.green)),
                      const Divider(),
                      ...?((entry.details['earnings'] as List?)?.map((e) => _buildReceiptRow(e['name'], e['amount'], true))),
                      const Divider(),
                      _buildReceiptRow('Gross Earnings', entry.grossEarnings, true, isBold: true),
                      const SizedBox(height: 32),
                      // DEDUCTIONS
                      const Text('DEDUCTIONS', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.red)),
                      const Divider(),
                      ...?((entry.details['deductions'] as List?)?.map((e) => _buildReceiptRow(e['name'], e['amount'], false))),
                      const Divider(),
                      _buildReceiptRow('Total Deductions', entry.totalDeductions, false, isBold: true),
                      const SizedBox(height: 32),
                      // NET PAY
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(colors: [Theme.of(context).primaryColor, Theme.of(context).primaryColor.withOpacity(0.8)]),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text('NET PAY', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                            Text(currencyFormatter.format(entry.netPay), style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildReceiptRow(String label, dynamic amount, bool isEarning, {bool isBold = false}) {
    final currencyFormatter = NumberFormat.currency(symbol: '\$');
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontWeight: isBold ? FontWeight.bold : FontWeight.normal, fontSize: isBold ? 16 : 14)),
          Text(
            currencyFormatter.format(amount),
            style: TextStyle(
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              fontSize: isBold ? 16 : 14,
              color: isBold ? (isEarning ? Colors.green[700] : Colors.red[700]) : null,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final emp = widget.employee;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : const Color(0xFF1E293B);

    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.employeeName} Profile', style: TextStyle(color: textColor)),
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        elevation: 0,
        iconTheme: IconThemeData(color: textColor),
        bottom: TabBar(
          controller: _tabController,
          labelColor: Theme.of(context).primaryColor,
          unselectedLabelColor: Colors.grey,
          indicatorColor: Theme.of(context).primaryColor,
          tabs: const [
            Tab(text: 'Attendance', icon: Icon(Icons.access_time)),
            Tab(text: 'Payslips', icon: Icon(Icons.receipt_long)),
          ],
        ),
      ),
      body: Column(
        children: [
          if (emp != null)
            Container(
              padding: const EdgeInsets.all(16.0),
              color: Theme.of(context).cardColor,
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 32,
                    backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
                    child: Text(
                      emp.firstName.isNotEmpty ? emp.firstName[0] : emp.username[0].toUpperCase(),
                      style: TextStyle(color: Theme.of(context).primaryColor, fontWeight: FontWeight.bold, fontSize: 24),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('${emp.firstName} ${emp.lastName}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        Text(emp.designation ?? 'No Designation', style: TextStyle(color: Colors.grey[600])),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Icon(Icons.business, size: 14, color: Colors.grey[500]),
                            const SizedBox(width: 4),
                            Text(emp.departmentName ?? emp.companyName, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                            const SizedBox(width: 16),
                            if (emp.phone != null) ...[
                              Icon(Icons.phone, size: 14, color: Colors.grey[500]),
                              const SizedBox(width: 4),
                              Text(emp.phone!, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                            ]
                          ],
                        )
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: emp.isActive ? Colors.green.withOpacity(0.1) : Colors.red.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      emp.isActive ? 'Active' : 'Inactive',
                      style: TextStyle(color: emp.isActive ? Colors.green[700] : Colors.red[700], fontWeight: FontWeight.bold, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildAttendanceTab(),
                _buildPayslipsTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
