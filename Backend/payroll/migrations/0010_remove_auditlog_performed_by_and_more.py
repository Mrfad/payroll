# Backend\payroll\migrations\0010_remove_auditlog_performed_by_and_more.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0008_alter_deviceconfiguration_company_and_more'),
        ('employees', '0001_initial'),
        ('payroll', '0009_alter_department_options_alter_shift_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auditlog',
            name='performed_by',
        ),
        migrations.RemoveField(
            model_name='auditlog',
            name='target_user',
        ),
        migrations.RemoveField(
            model_name='breakpolicy',
            name='company',
        ),
        migrations.RemoveField(
            model_name='shiftassignment',
            name='break_policies',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='company',
        ),
        migrations.RemoveField(
            model_name='overtimepolicy',
            name='company',
        ),
        migrations.RemoveField(
            model_name='leavetype',
            name='company',
        ),
        migrations.RemoveField(
            model_name='department',
            name='company',
        ),
        migrations.AlterField(
            model_name='salarycomponent',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.company'),
        ),
        migrations.AlterField(
            model_name='payrollperiod',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.company'),
        ),
        migrations.RemoveField(
            model_name='shift',
            name='company',
        ),
        migrations.AlterUniqueTogether(
            name='department',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='department',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='department',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='user',
        ),
        migrations.AlterField(
            model_name='payrollentry',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee'),
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='approved_by',
        ),
        migrations.AlterField(
            model_name='employeesalarystructure',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee'),
        ),
        migrations.RemoveField(
            model_name='leavebalance',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='shiftassignment',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='leavebalance',
            name='leave_type',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='leave_type',
        ),
        migrations.RemoveField(
            model_name='shiftassignment',
            name='overtime_policy',
        ),
        migrations.AlterUniqueTogether(
            name='shift',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='shiftassignment',
            name='shift',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='AttendanceRecord',
                ),
                migrations.DeleteModel(
                    name='AuditLog',
                ),
                migrations.DeleteModel(
                    name='BreakPolicy',
                ),
                migrations.DeleteModel(
                    name='Company',
                ),
                migrations.DeleteModel(
                    name='Department',
                ),
                migrations.DeleteModel(
                    name='Employee',
                ),
                migrations.DeleteModel(
                    name='LeaveBalance',
                ),
                migrations.DeleteModel(
                    name='LeaveRequest',
                ),
                migrations.DeleteModel(
                    name='LeaveType',
                ),
                migrations.DeleteModel(
                    name='OvertimePolicy',
                ),
                migrations.DeleteModel(
                    name='Shift',
                ),
                migrations.DeleteModel(
                    name='ShiftAssignment',
                ),
                migrations.DeleteModel(
                    name='UserProfile',
                ),
            ],
        ),
    ]
