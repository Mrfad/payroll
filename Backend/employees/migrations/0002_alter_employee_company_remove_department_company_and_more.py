# Backend\employees\migrations\0002_alter_employee_company_remove_department_company_and_more.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_alter_breakpolicy_company_alter_leavetype_company_and_more'),
        ('companies', '0001_initial'),
        ('device', '0009_alter_deviceconfiguration_company'),
        ('employees', '0001_initial'),
        ('payroll', '0011_alter_payrollperiod_company_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
        migrations.AlterUniqueTogether(
            name='department',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='department',
            name='company',
        ),
        migrations.RemoveField(
            model_name='department',
            name='parent',
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='companies.department'),
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.AddField(
            model_name='employee',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='companies.branch'),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='AuditLog',
                ),
                migrations.DeleteModel(
                    name='Company',
                ),
                migrations.DeleteModel(
                    name='Department',
                ),
                migrations.DeleteModel(
                    name='UserProfile',
                ),
            ],
        ),
    ]
