import 'package:flutter/material.dart';

class ReportsPage extends StatelessWidget {
  const ReportsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : const Color(0xFF1E293B);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Reports', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: textColor)),
        const SizedBox(height: 24),
        Expanded(
          child: Center(
            child: Text('Reports & Analytics Content Goes Here', style: TextStyle(color: textColor.withOpacity(0.6))),
          ),
        ),
      ],
    );
  }
}
