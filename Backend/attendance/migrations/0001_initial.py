# Backend\attendance\migrations\0001_initial.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BreakPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('break_start', models.TimeField(blank=True, null=True)),
                ('break_end', models.TimeField(blank=True, null=True)),
                ('duration_minutes', models.PositiveIntegerField(blank=True, null=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.company')),
            ],
            options={
                'db_table': 'payroll_breakpolicy',
            },
        ),
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('is_paid', models.BooleanField(default=True)),
                ('accrual_rule', models.JSONField(blank=True, default=dict)),
                ('max_balance', models.DecimalField(decimal_places=1, max_digits=5, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.company')),
            ],
            options={
                'db_table': 'payroll_leavetype',
            },
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('reason', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('deduction_days', models.DecimalField(decimal_places=1, default=0, max_digits=4)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leaves', to='employees.employee')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
                ('leave_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.leavetype')),
            ],
            options={
                'db_table': 'payroll_leaverequest',
            },
        ),
        migrations.CreateModel(
            name='LeaveBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_balance', models.DecimalField(decimal_places=1, max_digits=5)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
                ('leave_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.leavetype')),
            ],
            options={
                'db_table': 'payroll_leavebalance',
            },
        ),
        migrations.CreateModel(
            name='OvertimePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('daily_threshold_hours', models.DecimalField(decimal_places=2, max_digits=4)),
                ('weekly_threshold_hours', models.DecimalField(decimal_places=2, max_digits=4, null=True)),
                ('rate_multiplier', models.DecimalField(decimal_places=2, default=1.5, max_digits=3)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.company')),
            ],
            options={
                'db_table': 'payroll_overtimepolicy',
            },
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.company')),
            ],
            options={
                'db_table': 'payroll_shift',
                'unique_together': {('company', 'name')},
            },
        ),
        migrations.CreateModel(
            name='ShiftAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('break_policies', models.ManyToManyField(blank=True, to='attendance.breakpolicy')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
                ('overtime_policy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.overtimepolicy')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.shift')),
            ],
            options={
                'db_table': 'payroll_shiftassignment',
            },
        ),
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('first_in', models.DateTimeField(blank=True, null=True)),
                ('last_out', models.DateTimeField(blank=True, null=True)),
                ('break_start', models.DateTimeField(blank=True, null=True)),
                ('break_end', models.DateTimeField(blank=True, null=True)),
                ('total_work_seconds', models.PositiveIntegerField(default=0)),
                ('overtime_seconds', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('half_day', 'Half Day'), ('holiday', 'Holiday'), ('weekend', 'Weekend'), ('missing_punch', 'Missing Punch')], max_length=20)),
                ('is_anomaly', models.BooleanField(default=False)),
                ('anomaly_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
                ('shift_assignment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.shiftassignment')),
            ],
            options={
                'db_table': 'payroll_attendancerecord',
                'constraints': [models.UniqueConstraint(fields=('employee', 'date'), name='unique_attendance_per_day')],
            },
        ),
    ]
