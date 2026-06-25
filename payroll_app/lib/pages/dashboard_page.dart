import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../services/api_result.dart';
import '../services/websocket_service.dart';
import '../core/di/injection.dart';
import '../data/repositories/dashboard_repository.dart';
import 'dart:async';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  bool _isLoading = true;
  String _error = '';
  Map<String, dynamic> _data = {};
  StreamSubscription? _wsSubscription;

  @override
  void initState() {
    super.initState();
    _fetchData();
    _wsSubscription = getIt<WebSocketService>().updates.listen((event) {
      _fetchData(silent: true);
    });
  }

  @override
  void dispose() {
    _wsSubscription?.cancel();
    super.dispose();
  }

  Future<void> _fetchData({bool silent = false}) async {
    if (!silent) setState(() { _isLoading = true; _error = ''; });
    final result = await getIt<DashboardRepository>().getDashboardData();
    if (mounted) {
      if (result is ApiSuccess) {
        setState(() {
          _data = result.data;
          _isLoading = false;
        });
      } else if (result is ApiError) {
        if (!silent) {
          setState(() {
            _error = result.message;
            _isLoading = false;
          });
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : const Color(0xFF1E293B);
    final cardColor = Theme.of(context).cardColor;

    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error.isNotEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Failed to load dashboard: $_error', style: TextStyle(color: Colors.red, fontSize: 16)),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _fetchData, child: const Text('Retry')),
          ],
        ),
      );
    }

    final totalEmployees = _data['total_employees']?.toString() ?? '0';
    
    // Format currency
    final activePayrollRaw = _data['active_payroll'] ?? 0;
    final activePayroll = NumberFormat.currency(symbol: '\$').format(activePayrollRaw);
    
    final pendingRequests = _data['pending_requests']?.toString() ?? '0';
    final attendancePercentage = '${_data['attendance_percentage'] ?? 0}%';

    final isDesktop = MediaQuery.of(context).size.width >= 800;

    final kpiCards = [
      _buildKpiCard('Total Employees', totalEmployees, Icons.people_outline, Colors.blue, cardColor, textColor),
      _buildKpiCard('Active Payroll', activePayroll, Icons.monetization_on_outlined, Colors.green, cardColor, textColor),
      _buildKpiCard('Pending Requests', pendingRequests, Icons.pending_actions, Colors.orange, cardColor, textColor),
      _buildKpiCard('Today\'s Attendance', attendancePercentage, Icons.analytics_outlined, Colors.purple, cardColor, textColor),
    ];

    final chart1 = Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      color: cardColor,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Monthly Payroll Trend', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: textColor)),
            const SizedBox(height: 4),
            const Text('Last 6 months', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 20),
            SizedBox(height: 250, child: _buildLineChart(isDark, _data['monthly_trend'])),
          ],
        ),
      ),
    );

    final chart2 = Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      color: cardColor,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Department Distribution', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: textColor)),
            const SizedBox(height: 20),
            SizedBox(height: 250, child: _buildBarChart(_data['department_distribution'])),
          ],
        ),
      ),
    );

    final activityCard = Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      color: cardColor,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Recent Activity', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: textColor)),
            const SizedBox(height: 12),
            _buildActivityList(_data['recent_activity'], textColor),
          ],
        ),
      ),
    );

    return ListView(
      padding: const EdgeInsets.only(bottom: 24),
      children: [
        // KPI Cards
        if (isDesktop)
          Row(children: kpiCards)
        else
          Column(
            children: [
              Row(children: [kpiCards[0], kpiCards[1]]),
              const SizedBox(height: 16),
              Row(children: [kpiCards[2], kpiCards[3]]),
            ],
          ),
        const SizedBox(height: 24),

        // Charts
        if (isDesktop)
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(flex: 2, child: chart1),
              const SizedBox(width: 24),
              Expanded(flex: 1, child: chart2),
            ],
          )
        else
          Column(
            children: [
              chart1,
              const SizedBox(height: 24),
              chart2,
            ],
          ),
        const SizedBox(height: 24),

        // Activity
        activityCard,
      ],
    );
  }

  Widget _buildActivityList(List<dynamic>? activities, Color textColor) {
    if (activities == null || activities.isEmpty) {
      return const Center(child: Text('No recent activity.', style: TextStyle(color: Colors.grey)));
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: activities.length,
      itemBuilder: (context, index) {
        final activity = activities[index];
        final action = activity['action']?.toString() ?? 'UNKNOWN';
        final details = activity['details']?.toString() ?? '';
        
        Color color = Colors.grey;
        if (action == 'CREATE') color = Colors.green;
        else if (action == 'UPDATE') color = Colors.blue;
        else if (action == 'FREEZE') color = Colors.orange;
        else if (action == 'DELETE') color = Colors.red;

        String timeStr = 'Just now';
        if (activity['created_at'] != null) {
          final ts = DateTime.parse(activity['created_at']).toLocal();
          final diff = DateTime.now().difference(ts);
          if (diff.inDays > 0) timeStr = '${diff.inDays}d ago';
          else if (diff.inHours > 0) timeStr = '${diff.inHours}h ago';
          else if (diff.inMinutes > 0) timeStr = '${diff.inMinutes}m ago';
        }

        return _ActivityTile(details, timeStr, color, textColor);
      },
    );
  }

  Widget _buildKpiCard(String title, String value, IconData icon, Color color, Color cardColor, Color textColor) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.only(right: 16),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: cardColor,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    value,
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: textColor),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                  Text(
                    title,
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 2,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLineChart(bool isDark, List<dynamic>? trendData) {
    if (trendData == null || trendData.isEmpty) {
      return const Center(child: Text('No trend data available.'));
    }

    final lineColor = isDark ? const Color(0xFF60A5FA) : const Color(0xFF1E3C72);
    
    // Scale down the amounts for the chart to fit nicely
    double maxY = 0;
    List<FlSpot> spots = [];
    for (int i = 0; i < trendData.length; i++) {
      final item = trendData[i];
      final val = (item['amount'] as num).toDouble() / 1000000; // in Millions
      if (val > maxY) maxY = val;
      spots.add(FlSpot(i.toDouble(), val));
    }
    
    // If no data, use mock spots
    if (spots.isEmpty) {
      spots = const [FlSpot(0, 3.5), FlSpot(1, 4.0), FlSpot(2, 3.8), FlSpot(3, 5.0), FlSpot(4, 4.8), FlSpot(5, 6.2)];
      maxY = 7.0;
    }

    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        titlesData: FlTitlesData(
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final int idx = value.toInt();
                if (idx >= 0 && idx < trendData.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(trendData[idx]['month']?.toString() ?? '', style: const TextStyle(fontSize: 10, color: Colors.grey)),
                  );
                }
                return const Text('');
              },
            ),
          ),
          leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        minY: 0,
        maxY: maxY * 1.2,
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: lineColor,
            barWidth: 3,
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                colors: [
                  lineColor.withOpacity(0.3),
                  lineColor.withOpacity(0.0),
                ],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
            ),
            dotData: const FlDotData(show: true),
          ),
        ],
      ),
    );
  }

  Widget _buildBarChart(List<dynamic>? depts) {
    if (depts == null || depts.isEmpty) {
      return const Center(child: Text('No department data.'));
    }

    List<BarChartGroupData> groups = [];
    final colors = [Colors.blue, Colors.green, Colors.orange, Colors.purple, Colors.red, Colors.teal];
    
    double maxY = 0;
    for (int i = 0; i < depts.length; i++) {
      final count = (depts[i]['employee_count'] as num).toDouble();
      if (count > maxY) maxY = count;
      groups.add(_makeBar(i, count, colors[i % colors.length]));
    }

    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: maxY == 0 ? 10 : maxY * 1.2,
        barTouchData: BarTouchData(
          enabled: true,
          touchTooltipData: BarTouchTooltipData(
            getTooltipItem: (group, groupIndex, rod, rodIndex) {
              return BarTooltipItem(
                '${depts[groupIndex]['name']}\n${rod.toY.toInt()} Employees',
                const TextStyle(color: Colors.white),
              );
            },
          ),
        ),
        titlesData: FlTitlesData(
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final int idx = value.toInt();
                if (idx >= 0 && idx < depts.length) {
                  // Show max 3 chars
                  final name = depts[idx]['name']?.toString() ?? '';
                  final short = name.length > 3 ? name.substring(0, 3) : name;
                  return Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(short, style: const TextStyle(fontSize: 10, color: Colors.grey)),
                  );
                }
                return const Text('');
              },
            ),
          ),
          leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        gridData: const FlGridData(show: false),
        borderData: FlBorderData(show: false),
        barGroups: groups.isEmpty ? [_makeBar(0, 0, Colors.grey)] : groups,
      ),
    );
  }

  BarChartGroupData _makeBar(int x, double y, Color color) {
    return BarChartGroupData(
      x: x,
      barRods: [
        BarChartRodData(
          toY: y,
          color: color,
          width: 24,
          borderRadius: BorderRadius.circular(4),
        ),
      ],
    );
  }
}

class _ActivityTile extends StatelessWidget {
  final String text;
  final String time;
  final Color color;
  final Color textColor;

  const _ActivityTile(this.text, this.time, this.color, this.textColor);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(child: Text(text, style: TextStyle(fontWeight: FontWeight.w500, color: textColor))),
          Text(time, style: TextStyle(color: Colors.grey.shade500, fontSize: 12)),
        ],
      ),
    );
  }
}
