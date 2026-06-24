import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:payroll_desktop/services/api_service.dart';
import 'login_page.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  // Sidebar Menu Items
  final List<Map<String, dynamic>> _menuItems = const [
    {'icon': Icons.dashboard, 'label': 'Dashboard', 'active': true},
    {'icon': Icons.people, 'label': 'Employees', 'active': false},
    {'icon': Icons.calendar_today, 'label': 'Attendance', 'active': false},
    {'icon': Icons.beach_access, 'label': 'Leave', 'active': false},
    {'icon': Icons.monetization_on, 'label': 'Payroll', 'active': false},
    {'icon': Icons.bar_chart, 'label': 'Reports', 'active': false},
    {'icon': Icons.settings, 'label': 'Settings', 'active': false},
  ];

  void _handleLogout(BuildContext context) async {
    bool confirmed = await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Logout', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await ApiService.logout();
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const LoginPage()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9), // Light grey background
      body: Row(
        children: [
          // ----- SIDEBAR -----
          Container(
            width: 240,
            color: const Color(0xFF1E3C72), // Your dark blue brand color
            child: Column(
              children: [
                const SizedBox(height: 30),
                // Brand Logo
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    children: [
                      Icon(Icons.account_balance_wallet, color: Colors.white, size: 32),
                      SizedBox(width: 12),
                      Text(
                        'Payroll Pro',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 40),
                // Menu Items
                Expanded(
                  child: ListView.separated(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    itemCount: _menuItems.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (context, index) {
                      final item = _menuItems[index];
                      return Container(
                        decoration: BoxDecoration(
                          color: item['active'] ? Colors.white.withOpacity(0.15) : Colors.transparent,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: ListTile(
                          leading: Icon(item['icon'], color: Colors.white70),
                          title: Text(
                            item['label'],
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
                          ),
                          onTap: () {
                            // Implement navigation later
                          },
                        ),
                      );
                    },
                  ),
                ),
                // Sidebar Footer / Logout
                Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: ListTile(
                    leading: const Icon(Icons.logout, color: Colors.redAccent),
                    title: const Text('Logout', style: TextStyle(color: Colors.white)),
                    onTap: () => _handleLogout(context),
                  ),
                ),
              ],
            ),
          ),

          // ----- MAIN CONTENT -----
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Top App Bar area
                  Row(
                    children: [
                      const Text(
                        'Dashboard',
                        style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                      ),
                      const Spacer(),
                      // Search & Profile
                      Container(
                        width: 280,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.grey.shade300),
                        ),
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: const TextField(
                          decoration: InputDecoration(
                            icon: Icon(Icons.search, color: Colors.grey),
                            hintText: 'Search employees, payroll...',
                            border: InputBorder.none,
                          ),
                        ),
                      ),
                      const SizedBox(width: 20),
                      CircleAvatar(
                        radius: 20,
                        backgroundColor: const Color(0xFF1E3C72),
                        child: const Icon(Icons.person, color: Colors.white, size: 24),
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),

                  // KPI Cards
                  Expanded(
                    flex: 0,
                    child: Row(
                      children: [
                        _buildKpiCard('Total Employees', '1,240', Icons.people_outline, Colors.blue),
                        _buildKpiCard('Active Payroll', '₦4.8M', Icons.monetization_on_outlined, Colors.green),
                        _buildKpiCard('Pending Requests', '14', Icons.pending_actions, Colors.orange),
                        _buildKpiCard('Today\'s Attendance', '92%', Icons.analytics_outlined, Colors.purple),
                      ],
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Charts Row
                  Expanded(
                    flex: 2,
                    child: Row(
                      children: [
                        // Payroll Line Chart
                        Expanded(
                          flex: 2,
                          child: Card(
                            elevation: 0,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                            color: Colors.white,
                            child: Padding(
                              padding: const EdgeInsets.all(20.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text('Monthly Payroll Trend', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                                  const SizedBox(height: 4),
                                  const Text('Last 6 months', style: TextStyle(color: Colors.grey)),
                                  const SizedBox(height: 20),
                                  Expanded(child: _buildLineChart()),
                                ],
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 24),
                        // Department Distribution Bar Chart
                        Expanded(
                          flex: 1,
                          child: Card(
                            elevation: 0,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                            color: Colors.white,
                            child: Padding(
                              padding: const EdgeInsets.all(20.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text('Department Distribution', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                                  const SizedBox(height: 20),
                                  Expanded(child: _buildBarChart()),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Recent Activity Feed
                  Expanded(
                    flex: 1,
                    child: Card(
                      elevation: 0,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      color: Colors.white,
                      child: Padding(
                        padding: const EdgeInsets.all(20.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Recent Activity', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 12),
                            Expanded(
                              child: ListView(
                                children: const [
                                  _ActivityTile('John Doe submitted a leave request.', '2 hours ago', Colors.blue),
                                  _ActivityTile('Payroll for June was successfully processed.', '4 hours ago', Colors.green),
                                  _ActivityTile('Sarah Smith checked in (08:32 AM).', '6 hours ago', Colors.orange),
                                  _ActivityTile('New employee Michael Brown added to IT dept.', '1 day ago', Colors.purple),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ----- WIDGET HELPERS -----

  Widget _buildKpiCard(String title, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.only(right: 16),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
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
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                Text(
                  title,
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 14),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLineChart() {
    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        titlesData: const FlTitlesData(show: false),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: const [
              FlSpot(0, 3.5),
              FlSpot(1, 4.0),
              FlSpot(2, 3.8),
              FlSpot(3, 5.0),
              FlSpot(4, 4.8),
              FlSpot(5, 6.2),
            ],
            isCurved: true,
            color: const Color(0xFF1E3C72),
            barWidth: 3,
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                colors: [
                  const Color(0xFF1E3C72).withOpacity(0.3),
                  const Color(0xFF1E3C72).withOpacity(0.0),
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

  Widget _buildBarChart() {
    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: 20,
        barTouchData: BarTouchData(enabled: false),
        titlesData: const FlTitlesData(show: false),
        gridData: const FlGridData(show: false),
        borderData: FlBorderData(show: false),
        barGroups: [
          _makeBar(0, 18, Colors.blue),
          _makeBar(1, 12, Colors.green),
          _makeBar(2, 8, Colors.orange),
          _makeBar(3, 5, Colors.purple),
        ],
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

  const _ActivityTile(this.text, this.time, this.color);

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
          Expanded(child: Text(text, style: const TextStyle(fontWeight: FontWeight.w500))),
          Text(time, style: TextStyle(color: Colors.grey.shade500, fontSize: 12)),
        ],
      ),
    );
  }
}