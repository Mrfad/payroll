import 'dart:async';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../services/api_result.dart';
import '../services/websocket_service.dart';
import '../core/di/injection.dart';
import '../data/repositories/employee_repository.dart';

class AuditLogsPage extends StatefulWidget {
  final int? targetUserId;
  const AuditLogsPage({super.key, this.targetUserId});

  @override
  State<AuditLogsPage> createState() => _AuditLogsPageState();
}

class _AuditLogsPageState extends State<AuditLogsPage> {
  List<dynamic> _logs = [];
  bool _isLoading = true;
  StreamSubscription? _wsSubscription;

  @override
  void initState() {
    super.initState();
    _fetchLogs();
    _wsSubscription = WebSocketService().updates.listen((event) {
      if (event['model'] == 'AuditLog') {
        _fetchLogsSilently();
      }
    });
  }

  @override
  void dispose() {
    _wsSubscription?.cancel();
    super.dispose();
  }

  Future<void> _fetchLogsSilently() async {
    try {
      final response = await getIt<EmployeeRepository>().getAuditLogs(targetUserId: widget.targetUserId);
      if (response is ApiSuccess && mounted) {
        setState(() {
          if (response.data is Map && response.data.containsKey('results')) {
            _logs = response.data['results'];
          } else if (response.data is List) {
            _logs = response.data;
          }
        });
      }
    } catch (_) {}
  }

  Future<void> _fetchLogs() async {
    setState(() => _isLoading = true);
    try {
      final response = await getIt<EmployeeRepository>().getAuditLogs(targetUserId: widget.targetUserId);
      if (response is ApiSuccess) {
        setState(() {
          if (response.data is Map && response.data.containsKey('results')) {
            _logs = response.data['results'];
          } else if (response.data is List) {
            _logs = response.data;
          }
        });
      }
    } catch (e) {
      debugPrint('Error fetching audit logs: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : const Color(0xFF1E293B);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _fetchLogs,
              tooltip: 'Refresh',
            ),
          ],
        ),
        const SizedBox(height: 16),
        Expanded(
          child: Card(
            elevation: 0,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            color: Theme.of(context).cardColor,
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _logs.isEmpty
                    ? Center(child: Text('No audit logs found.', style: TextStyle(color: textColor)))
                    : LayoutBuilder(
                        builder: (context, constraints) {
                          return SingleChildScrollView(
                            scrollDirection: Axis.vertical,
                            child: SingleChildScrollView(
                              scrollDirection: Axis.horizontal,
                              child: ConstrainedBox(
                                constraints: BoxConstraints(minWidth: constraints.maxWidth),
                                child: DataTable(
                              headingRowColor: WidgetStateProperty.resolveWith((states) => Theme.of(context).cardColor.withOpacity(0.8)),
                              columns: const [
                                DataColumn(label: Text('Timestamp', style: TextStyle(fontWeight: FontWeight.bold))),
                                DataColumn(label: Text('Action', style: TextStyle(fontWeight: FontWeight.bold))),
                                DataColumn(label: Text('Target User', style: TextStyle(fontWeight: FontWeight.bold))),
                                DataColumn(label: Text('Performed By', style: TextStyle(fontWeight: FontWeight.bold))),
                                DataColumn(label: Text('Details', style: TextStyle(fontWeight: FontWeight.bold))),
                              ],
                              rows: _logs.map((log) {
                                final ts = log['created_at'] != null ? DateTime.parse(log['created_at']) : null;
                                final tsStr = ts != null ? DateFormat('MMM d, y, h:mm a').format(ts.toLocal()) : 'N/A';
                                
                                return DataRow(cells: [
                                  DataCell(Text(tsStr)),
                                  DataCell(
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: _getActionColor(log['action']).withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Text(
                                        log['action']?.toString() ?? 'N/A',
                                        style: TextStyle(color: _getActionColor(log['action']), fontWeight: FontWeight.bold),
                                      ),
                                    ),
                                  ),
                                  DataCell(Text(log['target_username'] ?? 'User ID: ${log['target_user']}')),
                                  DataCell(Text(log['performed_by_username'] ?? 'User ID: ${log['performed_by'] ?? 'System'}')),
                                  DataCell(
                                    SizedBox(
                                      width: 400,
                                      child: Tooltip(
                                        message: log['details']?.toString() ?? '',
                                        child: Text(
                                          log['details']?.toString() ?? '',
                                          overflow: TextOverflow.ellipsis,
                                          maxLines: 2,
                                        ),
                                      ),
                                    ),
                                  ),
                                ]);
                              }).toList(),
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

  Color _getActionColor(String? action) {
    switch (action) {
      case 'CREATE': return Colors.green;
      case 'UPDATE': return Colors.blue;
      case 'FREEZE': return Colors.orange;
      case 'UNFREEZE': return Colors.teal;
      case 'DELETE': return Colors.red;
      default: return Colors.grey;
    }
  }
}
