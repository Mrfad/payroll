class Department {
  final int id;
  final String name;
  final int companyId;
  final int? parentId;

  Department({
    required this.id,
    required this.name,
    required this.companyId,
    this.parentId,
  });

  factory Department.fromJson(Map<String, dynamic> json) {
    return Department(
      id: json['id'],
      name: json['name'],
      companyId: json['company'],
      parentId: json['parent'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'company': companyId,
      'parent': parentId,
    };
  }
}
