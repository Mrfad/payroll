# Backend\payroll\migrations\0004_employee_deleted_at.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0003_auditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
