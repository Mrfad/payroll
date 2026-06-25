import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../domain/models/payroll_entry.dart';
import '../services/api_service.dart';
import '../services/api_result.dart';

class PayslipsPage extends StatefulWidget {
  const PayslipsPage({super.key});

  @override
  State<PayslipsPage> createState() => _PayslipsPageState();
}

class _PayslipsPageState extends State<PayslipsPage> {
  late Future<List<PayrollEntry>> _payslipsFuture;

  @override
  void initState() {
    super.initState();
    _fetchPayslips();
  }

  void _fetchPayslips() {
    setState(() {
      _payslipsFuture = ApiService.getPayrollEntries().then((result) {
        if (result is ApiSuccess) {
          final data = result.data['results'] as List;
          return data.map((json) => PayrollEntry.fromJson(json)).toList();
        } else {
          throw Exception((result as ApiError).message);
        }
      });
    });
  }

  void _showPayslipDetails(PayrollEntry entry) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _buildPayslipReceipt(entry),
    );
  }

  Widget _buildPayslipReceipt(PayrollEntry entry) {
    final currencyFormatter = NumberFormat.currency(symbol: '\$');
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Handle bar
          Container(
            margin: const EdgeInsets.symmetric(vertical: 12),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey[400],
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text('PAYSLIP', textAlign: TextAlign.center, style: TextStyle(fontSize: 16, letterSpacing: 2, fontWeight: FontWeight.bold, color: Colors.grey)),
                  const SizedBox(height: 8),
                  Text(
                    '${entry.periodStart} to ${entry.periodEnd}',
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 24),
                  
                  // Employee Info
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        CircleAvatar(
                          backgroundColor: Theme.of(context).primaryColor,
                          child: Text(entry.employeeName[0].toUpperCase(), style: const TextStyle(color: Colors.white)),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(entry.employeeName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                              Text('Employee ID: ${entry.employeeId}', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 32),
                  
                  // EARNINGS
                  const Text('EARNINGS', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.green)),
                  const Divider(),
                  ...?((entry.details['earnings'] as List?)?.map((e) => _buildReceiptRow(e['name'], e['amount'], true))),
                  const Divider(),
                  _buildReceiptRow('Gross Earnings', entry.grossEarnings, true, isBold: true),
                  
                  const SizedBox(height: 32),
                  
                  // DEDUCTIONS
                  const Text('DEDUCTIONS', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.red)),
                  const Divider(),
                  ...?((entry.details['deductions'] as List?)?.map((e) => _buildReceiptRow(e['name'], e['amount'], false))),
                  const Divider(),
                  _buildReceiptRow('Total Deductions', entry.totalDeductions, false, isBold: true),
                  
                  const SizedBox(height: 32),
                  
                  // NET PAY
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [Theme.of(context).primaryColor, Theme.of(context).primaryColor.withOpacity(0.8)],
                      ),
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: Theme.of(context).primaryColor.withOpacity(0.3),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        )
                      ]
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('NET PAY', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                        Text(currencyFormatter.format(entry.netPay), style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReceiptRow(String label, dynamic amount, bool isEarning, {bool isBold = false}) {
    final currencyFormatter = NumberFormat.currency(symbol: '\$');
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontWeight: isBold ? FontWeight.bold : FontWeight.normal, fontSize: isBold ? 16 : 14)),
          Text(
            currencyFormatter.format(amount),
            style: TextStyle(
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              fontSize: isBold ? 16 : 14,
              color: isBold ? (isEarning ? Colors.green[700] : Colors.red[700]) : null,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : const Color(0xFF1E293B);
    final currencyFormatter = NumberFormat.currency(symbol: '\$');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('My Payslips', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: textColor)),
            IconButton(icon: const Icon(Icons.refresh), onPressed: _fetchPayslips),
          ],
        ),
        const SizedBox(height: 24),
        Expanded(
          child: FutureBuilder<List<PayrollEntry>>(
            future: _payslipsFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              } else if (snapshot.hasError) {
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.error_outline, color: Colors.red[400], size: 48),
                      const SizedBox(height: 16),
                      Text('Error loading payslips', style: TextStyle(color: textColor, fontSize: 18)),
                      Text(snapshot.error.toString(), style: const TextStyle(color: Colors.grey)),
                      const SizedBox(height: 16),
                      ElevatedButton(onPressed: _fetchPayslips, child: const Text('Try Again'))
                    ],
                  ),
                );
              } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.receipt_long, color: Colors.grey[400], size: 64),
                      const SizedBox(height: 16),
                      Text('No payslips available yet', style: TextStyle(color: textColor, fontSize: 18)),
                    ],
                  ),
                );
              }

              final entries = snapshot.data!;
              return ListView.builder(
                itemCount: entries.length,
                itemBuilder: (context, index) {
                  final entry = entries[index];
                  return Card(
                    elevation: 2,
                    margin: const EdgeInsets.only(bottom: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    child: InkWell(
                      borderRadius: BorderRadius.circular(16),
                      onTap: () => _showPayslipDetails(entry),
                      child: Padding(
                        padding: const EdgeInsets.all(20.0),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      color: Theme.of(context).primaryColor.withOpacity(0.1),
                                      shape: BoxShape.circle,
                                    ),
                                    child: Icon(Icons.account_balance_wallet, color: Theme.of(context).primaryColor),
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('Salary / Month', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                                        const SizedBox(height: 4),
                                        Text(
                                          '${entry.periodStart} - ${entry.periodEnd}', 
                                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 8),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text(currencyFormatter.format(entry.netPay), style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.green[700])),
                                const SizedBox(height: 4),
                                Row(
                                  children: [
                                    const Text('View details', style: TextStyle(fontSize: 12, color: Colors.blue)),
                                    const SizedBox(width: 4),
                                    const Icon(Icons.chevron_right, size: 14, color: Colors.blue),
                                  ],
                                )
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ),
      ],
    );
  }
}
