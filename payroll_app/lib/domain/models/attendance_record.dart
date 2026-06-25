class AttendanceRecord {
  final int id;
  final int employeeId;
  final String employeeName;
  final String employeeExternalId;
  final String date;
  final String? firstIn;
  final String? lastOut;
  final int totalWorkSeconds;
  final int overtimeSeconds;
  final String status;
  final bool isAnomaly;
  final String? anomalyReason;
  final String? punchedFrom;

  AttendanceRecord({
    required this.id,
    required this.employeeId,
    required this.employeeName,
    required this.employeeExternalId,
    required this.date,
    this.firstIn,
    this.lastOut,
    required this.totalWorkSeconds,
    required this.overtimeSeconds,
    required this.status,
    this.isAnomaly = false,
    this.anomalyReason,
    this.punchedFrom,
  });

  factory AttendanceRecord.fromJson(Map<String, dynamic> json) {
    return AttendanceRecord(
      id: json['id'],
      employeeId: json['employee'],
      employeeName: json['employee_name'] ?? 'Unknown',
      employeeExternalId: json['employee_external_id'] ?? '',
      date: json['date'] ?? '',
      firstIn: json['first_in'],
      lastOut: json['last_out'],
      totalWorkSeconds: json['total_work_seconds'] ?? 0,
      overtimeSeconds: json['overtime_seconds'] ?? 0,
      status: json['status'] ?? 'absent',
      isAnomaly: json['is_anomaly'] ?? false,
      anomalyReason: json['anomaly_reason'],
      punchedFrom: json['punched_from'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'employee': employeeId,
      'employee_name': employeeName,
      'employee_external_id': employeeExternalId,
      'date': date,
      'first_in': firstIn,
      'last_out': lastOut,
      'total_work_seconds': totalWorkSeconds,
      'overtime_seconds': overtimeSeconds,
      'status': status,
    };
  }
}
