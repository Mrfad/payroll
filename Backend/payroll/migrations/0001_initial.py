# Backend\payroll\migrations\0001_initial.py
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('device', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
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
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.company')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.company')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.department')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee_id', models.CharField(max_length=50, unique=True)),
                ('device_user_ids', models.JSONField(blank=True, default=dict)),
                ('designation', models.CharField(blank=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='employee_profiles/')),
                ('base_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.company')),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.department')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
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
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.company')),
            ],
            options={
                'abstract': False,
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
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leaves', to='payroll.employee')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.employee')),
                ('leave_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.leavetype')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LeaveBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_balance', models.DecimalField(decimal_places=1, max_digits=5)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.employee')),
                ('leave_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.leavetype')),
            ],
            options={
                'abstract': False,
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
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.company')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PayrollPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(default='open', max_length=20)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.company')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PayrollRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('run_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='draft', max_length=20)),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.payrollperiod')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PayrollEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('gross_earnings', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total_deductions', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('net_pay', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('details', models.JSONField(blank=True, default=dict)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.employee')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='payroll.payrollrun')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SalaryComponent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('component_type', models.CharField(choices=[('earning', 'Earning'), ('deduction', 'Deduction')], max_length=20)),
                ('calculation_method', models.CharField(default='fixed', help_text='fixed, percentage, or a callable string', max_length=50)),
                ('formula', models.TextField(blank=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.company')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmployeeSalaryStructure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('effective_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.employee')),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.salarycomponent')),
            ],
            options={
                'abstract': False,
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
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.company')),
            ],
            options={
                'abstract': False,
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
                ('break_policies', models.ManyToManyField(blank=True, to='payroll.breakpolicy')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.employee')),
                ('overtime_policy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.overtimepolicy')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.shift')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('first_in', models.DateTimeField(null=True)),
                ('last_out', models.DateTimeField(null=True)),
                ('break_start', models.DateTimeField(null=True)),
                ('break_end', models.DateTimeField(null=True)),
                ('total_work_seconds', models.PositiveIntegerField(default=0)),
                ('overtime_seconds', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('half_day', 'Half Day'), ('holiday', 'Holiday'), ('weekend', 'Weekend')], max_length=20)),
                ('raw_logs', models.ManyToManyField(blank=True, to='device.rawattendancelog')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.employee')),
                ('shift_assignment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.shiftassignment')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
