class PayrollEntry {
  final int id;
  final int employeeId;
  final String employeeName;
  final String periodStart;
  final String periodEnd;
  final double grossEarnings;
  final double totalDeductions;
  final double netPay;
  final Map<String, dynamic> details;

  PayrollEntry({
    required this.id,
    required this.employeeId,
    required this.employeeName,
    required this.periodStart,
    required this.periodEnd,
    required this.grossEarnings,
    required this.totalDeductions,
    required this.netPay,
    required this.details,
  });

  factory PayrollEntry.fromJson(Map<String, dynamic> json) {
    return PayrollEntry(
      id: json['id'],
      employeeId: json['employee'],
      employeeName: json['employee_name'] ?? 'Unknown',
      periodStart: json['period_start'] ?? '',
      periodEnd: json['period_end'] ?? '',
      grossEarnings: double.tryParse(json['gross_earnings']?.toString() ?? '0') ?? 0.0,
      totalDeductions: double.tryParse(json['total_deductions']?.toString() ?? '0') ?? 0.0,
      netPay: double.tryParse(json['net_pay']?.toString() ?? '0') ?? 0.0,
      details: json['details'] ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'employee': employeeId,
      'employee_name': employeeName,
      'period_start': periodStart,
      'period_end': periodEnd,
      'gross_earnings': grossEarnings,
      'total_deductions': totalDeductions,
      'net_pay': netPay,
      'details': details,
    };
  }
}
