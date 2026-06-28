# Backend\payroll\migrations\0011_alter_payrollperiod_company_and_more.py
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
        ('payroll', '0010_remove_auditlog_performed_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payrollperiod',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
        migrations.AlterField(
            model_name='salarycomponent',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
    ]
