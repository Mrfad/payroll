# Backend\payroll\migrations\0005_alter_attendancerecord_options_and_more.py
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0004_employee_deleted_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendancerecord',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='attendancerecord',
            unique_together={('employee', 'date')},
        ),
    ]
