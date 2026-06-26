import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../theme/theme_provider.dart';
import '../providers/auth_provider.dart';
import '../core/di/injection.dart';
import '../data/repositories/auth_repository.dart';
import 'login_page.dart';
import 'dashboard_page.dart';
import 'employees_page.dart';
import 'attendance_page.dart';
import 'leave_page.dart';
import 'payslips_page.dart';
import 'reports_page.dart';
import 'settings_page.dart';
import 'audit_logs_page.dart';
import 'about_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _selectedIndex = 0;

  final List<Map<String, dynamic>> _allMenuItems = const [
    {'icon': Icons.dashboard, 'label': 'Dashboard', 'perm': 'payroll.view_employee'},
    {'icon': Icons.people, 'label': 'Employees', 'perm': 'payroll.view_employee'},
    {'icon': Icons.calendar_today, 'label': 'Attendance', 'perm': 'payroll.view_attendancerecord'},
    {'icon': Icons.beach_access, 'label': 'Leave', 'perm': 'payroll.view_leaverequest'},
    {'icon': Icons.monetization_on, 'label': 'My Payslips', 'perm': null},
    {'icon': Icons.bar_chart, 'label': 'Reports', 'perm': 'payroll.view_payrollrun'},
    {'icon': Icons.settings, 'label': 'Settings', 'perm': 'auth.change_user'},
    {'icon': Icons.info, 'label': 'About', 'perm': null},
  ];

  final List<Widget> _allPages = const [
    DashboardPage(),
    EmployeesPage(),
    AttendancePage(),
    LeavePage(),
    PayslipsPage(),
    ReportsPage(),
    SettingsPage(),
    AboutPage(),
  ];

  @override
  void initState() {
    super.initState();
    // Fetch theme and permissions on load
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ThemeProvider>(context, listen: false).fetchTheme();
      Provider.of<AuthProvider>(context, listen: false).loadPermissions();
    });
  }

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
    ) ?? false;

    if (confirmed) {
      await getIt<AuthRepository>().logout();
      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const LoginPage()),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final themeProvider = Provider.of<ThemeProvider>(context);
    final isDark = themeProvider.isDarkMode;
    final scaffoldBg = Theme.of(context).scaffoldBackgroundColor;
    final sidebarColor = isDark ? const Color(0xFF1E293B) : const Color(0xFF1E3C72);
    final textColor = isDark ? Colors.white : const Color(0xFF1E293B);

    final List<Map<String, dynamic>> visibleMenu = [];
    final List<Widget> visiblePages = [];

    for (int i = 0; i < _allMenuItems.length; i++) {
      final perm = _allMenuItems[i]['perm'];
      if (perm == null || authProvider.hasPermission(perm)) {
        visibleMenu.add(_allMenuItems[i]);
        visiblePages.add(_allPages[i]);
      }
    }

    if (authProvider.isManagerOrDeveloper) {
      visibleMenu.add({'icon': Icons.security, 'label': 'Audit Logs'});
      visiblePages.add(const AuditLogsPage());
    }

    int currentIndex = _selectedIndex >= visibleMenu.length ? 0 : _selectedIndex;
    if (visibleMenu.isEmpty) {
      // Fallback if somehow empty
      visibleMenu.add({'icon': Icons.lock, 'label': 'Restricted Area'});
      visiblePages.add(Center(child: Text('You do not have access to any modules.\nPlease contact HR.', style: TextStyle(fontSize: 20, color: textColor))));
      currentIndex = 0;
    }

    final isDesktop = MediaQuery.of(context).size.width >= 800;

    final sidebarContent = Container(
      width: 240,
      color: sidebarColor,
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
                  'ShieldPay',
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
              itemCount: visibleMenu.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, index) {
                final item = visibleMenu[index];
                final isActive = index == currentIndex;
                return Container(
                  decoration: BoxDecoration(
                    color: isActive ? Colors.white.withOpacity(0.15) : Colors.transparent,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: ListTile(
                      leading: Icon(item['icon'], color: Colors.white70),
                      title: Text(
                        item['label'],
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
                      ),
                      onTap: () {
                        setState(() {
                          _selectedIndex = index;
                        });
                        if (!isDesktop) {
                          Navigator.pop(context); // Close drawer on mobile
                        }
                      },
                    ),
                  ),
                );
              },
            ),
          ),
          // Sidebar Footer / Logout
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Material(
              color: Colors.transparent,
              child: ListTile(
                leading: const Icon(Icons.logout, color: Colors.redAccent),
                title: const Text('Logout', style: TextStyle(color: Colors.white)),
                onTap: () => _handleLogout(context),
              ),
            ),
          ),
        ],
      ),
    );

    final mainContent = Padding(
      padding: EdgeInsets.all(isDesktop ? 24.0 : 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top App Bar area
          Row(
            children: [
              if (!isDesktop)
                Builder(
                  builder: (ctx) => IconButton(
                    icon: Icon(Icons.menu, color: textColor),
                    onPressed: () => Scaffold.of(ctx).openDrawer(),
                  ),
                ),
              Expanded(
                child: Text(
                  visibleMenu[currentIndex]['label'],
                  style: TextStyle(fontSize: isDesktop ? 28 : 22, fontWeight: FontWeight.bold, color: textColor),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              // Theme Toggle
              IconButton(
                icon: Icon(isDark ? Icons.light_mode : Icons.dark_mode, color: textColor),
                onPressed: () {
                  themeProvider.toggleTheme(!isDark);
                },
              ),
              if (isDesktop) const SizedBox(width: 20),
              // Profile
              if (isDesktop)
                Row(
                  children: [
                    Text(
                      authProvider.username ?? 'User',
                      style: TextStyle(color: textColor, fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                    const SizedBox(width: 12),
                    CircleAvatar(
                      radius: 20,
                      backgroundColor: sidebarColor,
                      child: const Icon(Icons.person, color: Colors.white, size: 24),
                    ),
                  ],
                ),
            ],
          ),
          SizedBox(height: isDesktop ? 32 : 16),

          // Page Content
          Expanded(
            child: IndexedStack(
              index: currentIndex,
              children: visiblePages,
            ),
          ),
        ],
      ),
    );

    return Scaffold(
      backgroundColor: scaffoldBg,
      drawer: isDesktop ? null : Drawer(child: sidebarContent),
      body: isDesktop
          ? Row(
              children: [
                sidebarContent,
                Expanded(child: mainContent),
              ],
            )
          : SafeArea(child: mainContent),
    );
  }
}
