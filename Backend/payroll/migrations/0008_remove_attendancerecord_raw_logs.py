# Backend\payroll\migrations\0008_remove_attendancerecord_raw_logs.py
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0007_attendancerecord_anomaly_reason_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendancerecord',
            name='raw_logs',
        ),
    ]
