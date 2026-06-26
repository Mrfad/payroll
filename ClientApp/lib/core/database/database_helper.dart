import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'dart:io';
import 'dart:convert';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  factory DatabaseHelper() => _instance;

  static Database? _database;

  DatabaseHelper._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    if (Platform.isWindows || Platform.isLinux) {
      sqfliteFfiInit();
      databaseFactory = databaseFactoryFfi;
    }
    
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'payroll_offline.db');

    return await openDatabase(
      path,
      version: 2,
      onCreate: _onCreate,
      onUpgrade: (db, oldVersion, newVersion) async {
        if (oldVersion < 2) {
          await db.execute('DROP TABLE IF EXISTS employees');
          await db.execute('DROP TABLE IF EXISTS companies');
          await db.execute('DROP TABLE IF EXISTS departments');
          await db.execute('DROP TABLE IF EXISTS offline_mutations');
          await _onCreate(db, newVersion);
        }
      }
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE employees (
        id INTEGER PRIMARY KEY,
        employee_id TEXT,
        username TEXT,
        email TEXT,
        first_name TEXT,
        last_name TEXT,
        company_id INTEGER,
        company_name TEXT,
        department_id INTEGER,
        department_name TEXT,
        is_active INTEGER,
        deleted_at TEXT,
        created_at TEXT,
        updated_at TEXT,
        device_user_ids TEXT,
        designation TEXT,
        phone TEXT,
        profile_picture TEXT,
        base_salary TEXT,
        user INTEGER,
        company INTEGER,
        department INTEGER
      )
    ''');

    await db.execute('''
      CREATE TABLE companies (
        id INTEGER PRIMARY KEY,
        name TEXT
      )
    ''');

    await db.execute('''
      CREATE TABLE departments (
        id INTEGER PRIMARY KEY,
        name TEXT,
        company_id INTEGER
      )
    ''');

    await db.execute('''
      CREATE TABLE offline_mutations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint TEXT,
        method TEXT,
        payload TEXT,
        created_at TEXT
      )
    ''');
  }

  Future<void> clearTable(String tableName) async {
    final db = await database;
    await db.delete(tableName);
  }

  Future<void> insertBatch(String tableName, List<Map<String, dynamic>> items) async {
    final db = await database;
    Batch batch = db.batch();
    for (var item in items) {
      final sanitizedItem = <String, dynamic>{};
      item.forEach((key, value) {
        if (value is bool) {
          sanitizedItem[key] = value ? 1 : 0;
        } else if (value is Map || value is List) {
           sanitizedItem[key] = jsonEncode(value);
        } else {
           sanitizedItem[key] = value;
        }
      });
      batch.insert(tableName, sanitizedItem, conflictAlgorithm: ConflictAlgorithm.replace);
    }
    await batch.commit(noResult: true);
  }

  Future<List<Map<String, dynamic>>> queryAll(String tableName) async {
    final db = await database;
    return await db.query(tableName);
  }

  Future<void> insertMutation(String endpoint, String method, String payload) async {
    final db = await database;
    await db.insert('offline_mutations', {
      'endpoint': endpoint,
      'method': method,
      'payload': payload,
      'created_at': DateTime.now().toIso8601String(),
    });
  }
}
