class Employee {
  final int id;
  final String username;
  final String firstName;
  final String lastName;
  final String employeeId;
  final String companyName;
  final String? departmentName;
  final String? designation;
  final String? phone;
  final bool isActive;
  final String? baseSalary;

  Employee({
    required this.id,
    required this.username,
    required this.firstName,
    required this.lastName,
    required this.employeeId,
    required this.companyName,
    this.departmentName,
    this.designation,
    this.phone,
    this.isActive = true,
    this.baseSalary,
  });

  factory Employee.fromJson(Map<String, dynamic> json) {
    return Employee(
      id: json['id'],
      username: json['username'] ?? '',
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      employeeId: json['employee_id'] ?? '',
      companyName: json['company_name'] ?? '',
      departmentName: json['department_name'],
      designation: json['designation'],
      phone: json['phone'],
      isActive: json['is_active'] ?? true,
      baseSalary: json['base_salary']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'first_name': firstName,
      'last_name': lastName,
      'employee_id': employeeId,
      'company_name': companyName,
      'department_name': departmentName,
      'designation': designation,
      'phone': phone,
      'is_active': isActive,
      'base_salary': baseSalary,
    };
  }
}
